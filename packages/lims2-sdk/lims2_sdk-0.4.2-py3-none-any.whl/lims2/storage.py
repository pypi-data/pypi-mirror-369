"""存储服务模块

通过 STS 临时凭证上传文件到阿里云 OSS，支持大文件断点续传
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import oss2

from .exceptions import APIError
from .utils import (
    format_file_size,
    generate_unique_filename,
    get_file_size,
    handle_api_response,
)


class StorageService:
    """存储服务

    通过阿里云 OSS 提供文件存储功能，支持：
    - 大文件断点续传（>10MB）
    - STS 临时凭证安全上传
    - 文件元数据记录
    - 目录批量上传
    """

    def __init__(self, client):
        """初始化存储服务

        Args:
            client: Lims2Client 实例，提供配置和会话

        Raises:
            ValueError: 当必需的配置项缺失时
        """
        self.client = client
        self.config = client.config
        self.session = client.session
        # STS 凭证缓存，避免频繁请求
        self._sts_cache = {}

        # 校验必需的配置项
        required = ["api_url", "team_id", "token"]
        missing = [attr for attr in required if not getattr(self.config, attr, None)]
        if missing:
            raise ValueError(f"配置项缺失: {', '.join(missing)}")

    def upload_file(
        self,
        file_path: Union[str, Path],
        project_id: str,
        analysis_node: Optional[str] = None,
        file_category: Optional[str] = None,
        key: Optional[str] = None,
        sample_id: Optional[str] = None,
        description: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        base_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """上传单个文件到 OSS

        Args:
            file_path: 本地文件路径
            project_id: 项目 ID
            analysis_node: 分析节点名称
            file_category: 文件分类（如 'results', 'plot_data'）
            key: 自定义 OSS 键名，不提供则自动生成
            sample_id: 样本 ID（可选）
            description: 文件描述（可选）
            progress_callback: 进度回调函数，签名为 callback(consumed_bytes, total_bytes)
            base_path: OSS 中的基础路径（可选）

        Returns:
            Dict[str, Any]: 上传结果，包含文件信息和 OSS 键名

        Raises:
            FileNotFoundError: 文件不存在
            APIError: STS 凭证获取失败或 OSS 上传失败

        Example:
            >>> result = storage.upload_file(
            ...     "data.csv", "proj_001", "analysis1", "results",
            ...     progress_callback=lambda consumed, total: print(f"{consumed/total*100:.1f}%")
            ... )
            >>> print(result['oss_key'])
            biofile/proj_001/analysis1/data_123456.csv
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 构建 OSS 键名：biofile/project_id/[base_path/]filename
        if not key:
            # 如果没有指定 base_path，对单文件上传使用 analysis_node/sample_id 作为默认路径
            if base_path is None:
                path_parts = []
                if analysis_node:
                    path_parts.append(analysis_node)
                if sample_id:
                    path_parts.append(sample_id)
                base_path = "/".join(path_parts) if path_parts else None

            key = self._build_oss_key(project_id, file_path.name, base_path)

        # 获取 OSS bucket 并上传文件
        bucket = self._get_oss_bucket(project_id)
        self._upload_to_oss(bucket, file_path, key, progress_callback)

        # 在后端数据库记录文件信息
        return self._create_file_record(
            file_path,
            key,
            project_id,
            analysis_node or "files",
            file_category or "result",
            sample_id,
            description,
        )

    def upload_directory(
        self,
        dir_path: Union[str, Path],
        project_id: str,
        analysis_node: Optional[str] = None,
        file_category: Optional[str] = None,
        sample_id: Optional[str] = None,
        recursive: bool = True,
        base_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """批量上传目录中的所有文件

        Args:
            dir_path: 目录路径
            project_id: 项目 ID
            analysis_node: 分析节点名称
            file_category: 文件分类
            sample_id: 样本 ID（可选）
            recursive: 是否递归上传子目录（默认 True）
            base_path: OSS 中的基础路径（可选）

        Returns:
            List[Dict[str, Any]]: 每个文件的上传结果列表

        Raises:
            FileNotFoundError: 目录不存在
            ValueError: 路径不是目录

        Note:
            - 保持原目录结构上传到 OSS
            - 单个文件失败不影响其他文件
            - 返回结果包含成功和失败的文件信息

        Example:
            >>> results = storage.upload_directory(
            ...     "output/", "proj_001", "analysis1", "results"
            ... )
            >>> for result in results:
            ...     if 'error' in result:
            ...         print(f"失败: {result['file_path']} - {result['error']}")
            ...     else:
            ...         print(f"成功: {result['file_name']}")
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        if not dir_path.is_dir():
            raise ValueError(f"路径不是目录: {dir_path}")

        # 收集所有文件（递归或非递归）
        pattern = "**/*" if recursive else "*"
        files = [f for f in dir_path.glob(pattern) if f.is_file()]

        results = []
        for file_path in files:
            try:
                # 保持相对路径结构，包含原始目录名
                relative_path = file_path.relative_to(dir_path)
                # 添加原始目录名作为前缀
                dir_name = dir_path.name
                path_with_dir = f"{dir_name}/{relative_path}"
                key = self._build_oss_key(
                    project_id,
                    path_with_dir,
                    base_path,
                )

                # 上传单个文件（key已经包含完整路径，不需要再传base_path）
                result = self.upload_file(
                    file_path, project_id, analysis_node, file_category, key, sample_id
                )
                results.append(result)
            except Exception as e:
                # 记录失败的文件，继续处理其他文件
                results.append(
                    {"file_path": str(file_path), "error": str(e), "success": False}
                )

        return results

    def file_exists(self, oss_key: str, project_id: str) -> bool:
        """检查文件是否存在"""
        try:
            bucket = self._get_oss_bucket(project_id)
            return bucket.object_exists(oss_key)
        except Exception:
            return False

    def get_file_info(self, oss_key: str, project_id: str) -> Dict[str, Any]:
        """获取文件详细信息"""
        bucket = self._get_oss_bucket(project_id)

        try:
            obj_info = bucket.get_object_meta(oss_key)
            if obj_info is None:
                raise APIError(f"无法获取文件元数据: {oss_key}")

            content_type = getattr(obj_info, "content_type", None)
            etag = getattr(obj_info, "etag", None)
            content_length = getattr(obj_info, "content_length", 0)

            return self._parse_file_info(
                oss_key,
                content_length,
                obj_info.last_modified,
                project_id,
                content_type,
                etag,
            )
        except oss2.exceptions.NoSuchKey:
            raise FileNotFoundError(f"文件不存在: {oss_key}")

    def _get_oss_bucket(self, project_id: str) -> oss2.Bucket:
        """获取配置了 STS 认证的 OSS Bucket 对象

        Args:
            project_id: 项目 ID，用于获取对应的 STS 凭证

        Returns:
            oss2.Bucket: 配置了临时凭证的 Bucket 实例

        Raises:
            APIError: STS 凭证获取失败
        """
        sts_info = self._get_sts_token(project_id)
        auth = oss2.StsAuth(
            sts_info["access_key_id"],
            sts_info["access_key_secret"],
            sts_info["security_token"],
        )
        return oss2.Bucket(auth, sts_info["endpoint"], sts_info["bucket_name"])

    def _build_oss_key(
        self,
        project_id: str,
        filename: str,
        base_path: Optional[str] = None,
    ) -> str:
        """构建 OSS 文件键名

        生成规则：
        - 基础路径：biofile/project_id/[base_path/]
        - 文件名：添加随机后缀避免冲突
        - 始终保持目录结构

        Args:
            project_id: 项目 ID
            filename: 文件名或相对路径
            base_path: OSS 中的基础路径（可选）

        Returns:
            str: OSS 键名

        Example:
            >>> self._build_oss_key("proj_001", "data.csv", base_path="results")
            "biofile/proj_001/results/data_123456.csv"

            >>> self._build_oss_key("proj_001", "subdir/file.txt", "results")
            "biofile/proj_001/results/subdir/file_123456.txt"
        """
        parts = ["biofile", project_id]
        if base_path:
            parts.append(base_path)

        path_obj = Path(filename)
        if len(path_obj.parts) > 1:
            # 保持目录结构：包含子目录路径
            sub_dirs = "/".join(path_obj.parts[:-1])
            unique_filename = generate_unique_filename(path_obj.stem, path_obj.suffix)
            return "/".join(parts) + "/" + sub_dirs + "/" + unique_filename
        else:
            # 单文件：直接放在基础路径下
            unique_filename = generate_unique_filename(path_obj.stem, path_obj.suffix)
            return "/".join(parts) + "/" + unique_filename

    def _upload_to_oss(
        self,
        bucket: oss2.Bucket,
        file_path: Path,
        key: str,
        progress_callback: Optional[Callable] = None,
    ):
        """使用断点续传方式上传文件到 OSS

        Args:
            bucket: OSS Bucket 对象
            file_path: 本地文件路径
            key: OSS 文件键名
            progress_callback: 进度回调函数（可选）

        Note:
            - 超过 10MB 的文件自动使用分片上传
            - 每个分片 5MB，使用 3 个线程并发上传
            - 支持断点续传，中断后可恢复
            - 临时文件存储在 /tmp 目录
            - 上传完成后自动清理临时文件
        """
        temp_store = oss2.ResumableStore(root="/tmp")
        try:
            oss2.resumable_upload(
                bucket,
                key,
                str(file_path),
                store=temp_store,
                multipart_threshold=10 * 1024 * 1024,  # 10MB 阈值
                part_size=5 * 1024 * 1024,  # 5MB 分片
                num_threads=3,  # 3 线程并发
                progress_callback=progress_callback,
            )
        finally:
            # 清理断点续传的临时文件
            try:
                temp_store.remove(key)
            except Exception:
                pass

    def _create_file_record(
        self,
        file_path: Path,
        key: str,
        project_id: str,
        analysis_node: str,
        file_category: str,
        sample_id: Optional[str],
        description: Optional[str],
    ) -> Dict[str, Any]:
        """在后端数据库创建文件上传记录

        Args:
            file_path: 本地文件路径
            key: OSS 文件键名
            project_id: 项目 ID
            analysis_node: 分析节点名称
            file_category: 文件分类
            sample_id: 样本 ID（可选）
            description: 文件描述（可选）

        Returns:
            Dict[str, Any]: 包含文件信息的结果，OSS 上传成功但记录失败时包含 error 字段

        Note:
            - 即使数据库记录失败，OSS 上传已完成，文件仍可访问
            - 返回结果总是包含基本文件信息
            - API 失败时在 error 字段中包含错误信息
        """
        file_size = get_file_size(file_path)

        # 构建基本返回信息
        result = {
            "project_id": project_id,
            "file_name": file_path.name,
            "oss_key": key,
            "file_size": file_size,
            "file_size_readable": format_file_size(file_size),
            "file_category": file_category,
            "analysis_node": analysis_node,
        }

        # 记录到数据库
        record_data = {
            "project_id": project_id,
            "sample_id": sample_id,
            "oss_key": key,
            "file_name": file_path.name,
            "analysis_node": analysis_node,
            "file_category": file_category,
            "description": description or "",
            "file_size": file_size,
            "team_id": self.config.team_id,
            "token": self.config.token,
        }

        response = self.session.post(
            f"{self.config.api_url}/get_data/biofile/record_file_upload/",
            json=record_data,
            timeout=self.config.timeout,
        )

        response_data = handle_api_response(response, "文件记录创建")

        # 兼容不同的响应格式
        if "data" in response_data:
            file_record = response_data["data"]
        elif "record" in response_data:
            file_record = response_data["record"]
        else:
            file_record = response_data

        # 提取文件信息并添加到结果
        if file_record.get("file_id"):
            result["file_id"] = file_record["file_id"]
        if file_record.get("file_url"):
            result["file_url"] = file_record["file_url"]

        result["record_created"] = True

        return result

    def _parse_file_info(
        self,
        oss_key: str,
        size: int,
        last_modified,
        project_id: str,
        content_type: str = None,
        etag: str = None,
    ) -> Dict[str, Any]:
        """解析 OSS 文件元数据为标准格式

        Args:
            oss_key: OSS 文件键名
            size: 文件大小（字节）
            last_modified: 最后修改时间
            project_id: 项目 ID
            content_type: 内容类型（可选）
            etag: 文件 ETag（可选）

        Returns:
            Dict[str, Any]: 标准化的文件信息

        Note:
            - 自动解析键名中的 analysis_node 和 sample_id
            - 处理不同格式的时间戳
            - 键名格式：biofile/project_id/analysis_node/[sample_id]/filename
        """
        key_parts = oss_key.split("/")

        # 处理last_modified的不同格式
        if last_modified:
            if hasattr(last_modified, "isoformat"):
                last_modified_str = last_modified.isoformat()
            else:
                last_modified_str = str(last_modified)
        else:
            last_modified_str = None

        file_info = {
            "oss_key": oss_key,
            "file_name": Path(oss_key).name,
            "file_size": size,
            "file_size_readable": format_file_size(size),
            "last_modified": last_modified_str,
            "project_id": project_id,
        }

        # 添加可选字段
        if content_type:
            file_info["content_type"] = content_type
        if etag:
            file_info["etag"] = etag

        # 解析路径结构: biofile/project_id/analysis_node/[sample_id]/filename
        if len(key_parts) >= 4:
            file_info["analysis_node"] = key_parts[2]
            if len(key_parts) >= 5:
                file_info["sample_id"] = key_parts[3]

        return file_info

    def _get_sts_token(self, project_id: str) -> Dict[str, Any]:
        """获取阿里云 STS 临时访问凭证

        Args:
            project_id: 项目 ID

        Returns:
            Dict[str, Any]: STS 凭证信息，包含：
                - access_key_id: 临时访问密钥 ID
                - access_key_secret: 临时访问密钥
                - security_token: 安全令牌
                - endpoint: OSS 服务端点
                - bucket_name: OSS 存储桶名称

        Raises:
            APIError: 获取 STS 凭证失败

        Note:
            - 使用简单的内存缓存避免频繁请求
            - 缓存键格式：project_id:team_id
            - STS 凭证有时效性，过期后需重新获取
        """
        cache_key = f"{project_id}:{self.config.team_id}"

        # 简单缓存机制
        if cache_key in self._sts_cache:
            return self._sts_cache[cache_key]

        # 从 API 获取新的 STS 凭证
        params = {"team_id": self.config.team_id} if self.config.team_id else {}
        response = self.session.get(
            f"{self.config.api_url}/get_data/aliyun_sts/",
            params=params,
            timeout=self.config.timeout,
        )

        result = handle_api_response(response, "获取STS凭证")
        raw_data = result.get("record", result)

        # 构建标准化的凭证信息
        token_data = {
            "access_key_id": raw_data.get("AccessKeyId"),
            "access_key_secret": raw_data.get("AccessKeySecret"),
            "security_token": raw_data.get("SecurityToken"),
            "endpoint": self.config.oss_endpoint,
            "bucket_name": self.config.oss_bucket_name,
        }

        # 缓存凭证并返回
        self._sts_cache[cache_key] = token_data
        return token_data
