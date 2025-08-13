"""图表服务模块

基于原 biotree_chart 功能实现
"""

import gzip
from pathlib import Path
from typing import Any, Dict, Optional, Union

import orjson
import requests

from .exceptions import UploadError
from .utils import (
    format_file_size,
    generate_unique_filename,
    get_file_size,
    get_json_size,
    handle_api_response,
    read_file_content,
    round_floats,
)

# 内联存储阈值 200KB
INLINE_STORAGE_THRESHOLD = 200 * 1024


class ChartService:
    """图表服务"""

    def __init__(self, client):
        """初始化图表服务

        Args:
            client: Lims2Client 实例
        """
        self.client = client
        self.config = client.config
        self.session = client.session

    def upload(
        self,
        data_source: Union[Dict[str, Any], str, Path],
        project_id: str,
        chart_name: str,
        sample_id: Optional[str] = None,
        chart_type: Optional[str] = None,
        description: Optional[str] = None,
        contrast: Optional[str] = None,
        analysis_node: Optional[str] = None,
        precision: Optional[int] = None,
    ) -> Dict[str, Any]:
        """上传图表

        Args:
            data_source: 图表数据源，可以是字典、文件路径或 Path 对象
            project_id: 项目 ID
            chart_name: 图表名称
            sample_id: 样本 ID（可选）
            chart_type: 图表类型（可选）
            description: 图表描述（可选）
            contrast: 对比策略（可选）
            analysis_node: 分析节点名称（可选）
            precision: 浮点数精度控制，保留小数位数（0-10，默认3）

        Returns:
            上传结果
        """
        # 参数验证
        if not chart_name:
            raise ValueError("图表名称不能为空")
        if not project_id:
            raise ValueError("项目 ID 不能为空")
        if not data_source:
            raise ValueError("数据源不能为空")
        if precision is not None and not 0 <= precision <= 10:
            raise ValueError("precision 必须在 0-10 之间")

        # 构建请求数据
        request_data = {
            "chart_name": chart_name,
            "project_id": project_id,
            "chart_type": chart_type,
            "description": description,
        }

        # 添加可选参数
        if sample_id:
            request_data["sample_id"] = sample_id
        if contrast:
            request_data["contrast"] = contrast
        if analysis_node:
            request_data["analysis_node"] = analysis_node

        # 根据数据源类型处理
        if isinstance(data_source, dict):
            return self._upload_from_dict(request_data, data_source, precision)
        elif isinstance(data_source, (str, Path)):
            return self._upload_from_file(request_data, data_source, precision)
        else:
            raise ValueError("数据源必须是字典、文件路径或 Path 对象")

    def _upload_from_dict(
        self,
        request_data: Dict[str, Any],
        chart_data: Dict[str, Any],
        precision: Optional[int] = None,
    ) -> Dict[str, Any]:
        """从字典数据上传图表"""
        # 检测渲染器类型
        if "data" in chart_data and "layout" in chart_data:
            request_data["renderer_type"] = "plotly"
        elif "elements" in chart_data or (
            "nodes" in chart_data and "edges" in chart_data
        ):
            request_data["renderer_type"] = "cytoscape"
        else:
            raise ValueError("不支持的图表数据格式")

        # 应用精度控制（默认使用 3 位小数）
        if precision is None:
            precision = 3  # 默认精度为 3

        # 检测到 Plotly 图表时进行清理
        if request_data["renderer_type"] == "plotly":
            if "layout" in chart_data and "template" in chart_data["layout"]:
                del chart_data["layout"]["template"]

        # 记录原始大小
        original_size = get_json_size(chart_data)

        # 应用精度控制
        chart_data = round_floats(chart_data, precision)

        # 序列化数据
        json_str = orjson.dumps(chart_data).decode("utf-8")
        file_size = len(json_str.encode("utf-8"))

        # 显示大小减少信息
        if file_size < original_size:
            reduction_percent = (1 - file_size / original_size) * 100
            print(
                f"精度控制: {format_file_size(original_size)} -> "
                f"{format_file_size(file_size)} "
                f"(减少 {reduction_percent:.1f}%)"
            )

        if file_size > INLINE_STORAGE_THRESHOLD:
            # 大数据压缩后上传到 OSS
            compressed_data = gzip.compress(json_str.encode("utf-8"))

            # 生成文件名
            filename = generate_unique_filename(request_data["chart_name"], "json.gz")

            # 获取签名 URL
            signed_url, oss_key = self._get_oss_signed_url(
                request_data["project_id"], request_data.get("sample_id"), filename
            )

            # 上传到 OSS
            if not self._upload_to_oss(signed_url, compressed_data, "application/gzip"):
                raise UploadError("上传到 OSS 失败")

            request_data["file_format"] = "json.gz"
            request_data["file_name"] = filename
            request_data["oss_key"] = oss_key
        else:
            # 小数据内联存储
            request_data["file_format"] = "json"
            request_data["chart_data"] = chart_data
            request_data["file_name"] = generate_unique_filename(
                request_data["chart_name"], "json"
            )

        # 创建图表记录
        return self._create_chart_record(request_data)

    def _upload_from_file(
        self,
        request_data: Dict[str, Any],
        file_path: Union[str, Path],
        precision: Optional[int] = None,
    ) -> Dict[str, Any]:
        """从文件上传图表"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_format = file_path.suffix.lower().strip(".")
        request_data["file_size"] = get_file_size(file_path)
        request_data["file_format"] = file_format

        # JSON 文件特殊处理
        if file_format == "json":
            try:
                chart_data = read_file_content(file_path)
                if isinstance(chart_data, dict):
                    return self._upload_from_dict(request_data, chart_data, precision)
            except FileNotFoundError:
                raise
            except orjson.JSONDecodeError as e:
                raise ValueError(f"JSON 文件格式错误: {e}")
            except Exception as e:
                raise ValueError(f"读取 JSON 文件失败: {e}")

        # 其他文件类型
        if file_format in ["png", "jpg", "jpeg", "svg", "pdf"]:
            request_data["renderer_type"] = "image"
        elif file_format == "html":
            request_data["renderer_type"] = "html"
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")

        # 生成文件名
        filename = generate_unique_filename(request_data["chart_name"], file_format)
        request_data["file_name"] = filename

        # 获取签名 URL
        signed_url, oss_key = self._get_oss_signed_url(
            request_data["project_id"], request_data.get("sample_id"), filename
        )

        # 读取文件内容
        file_content = read_file_content(file_path)
        if isinstance(file_content, dict):
            file_content = orjson.dumps(file_content)

        # 上传到 OSS
        content_type = self._get_content_type(file_format)
        if not self._upload_to_oss(signed_url, file_content, content_type):
            raise UploadError("上传到 OSS 失败")

        request_data["oss_key"] = oss_key

        # 创建图表记录
        return self._create_chart_record(request_data)

    def _get_oss_signed_url(
        self, project_id: str, sample_id: Optional[str], file_name: str
    ) -> tuple:
        """获取 OSS 签名 URL"""
        request_data = {"project_id": project_id, "file_name": file_name}

        if sample_id:
            request_data["sample_id"] = sample_id

        request_data["token"] = self.config.token
        request_data["team_id"] = self.config.team_id

        try:
            response = self.session.post(
                f"{self.config.api_url}/get_data/biochart/get_upload_url/",
                json=request_data,
                timeout=self.config.timeout,
            )
            result = handle_api_response(response, "获取上传签名 URL")
            return result["record"]["signed_url"], result["record"]["oss_key"]
        except Exception as e:
            # 对于批量上传时的连接错误，提供更详细的错误信息
            if "Name or service not known" in str(e):
                raise UploadError(
                    f"DNS 解析失败（批量上传时偶发）: {str(e)}\n"
                    f"建议：1) 使用客户端方法Lims2Client，复用链接池，不要使用便捷函数 2) 增加重试间隔 3) 检查本地DNS配置"
                )
            raise

    def _upload_to_oss(
        self,
        signed_url: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> bool:
        """上传数据到 OSS"""
        headers = {"Content-Type": content_type}
        # 使用独立会话，避免泄露认证信息
        with requests.Session() as session:
            response = session.put(
                signed_url, data=data, headers=headers, timeout=self.config.timeout
            )
            return response.status_code == 200

    def _create_chart_record(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建图表记录"""

        request_data["token"] = self.config.token
        request_data["team_id"] = self.config.team_id

        try:
            response = self.session.post(
                f"{self.config.api_url}/get_data/biochart/create_chart/",
                json=request_data,
                timeout=self.config.timeout,
            )
            return handle_api_response(response, "创建图表记录")
        except Exception as e:
            # 对于批量上传时的连接错误，提供更详细的错误信息
            if "Name or service not known" in str(e):
                raise UploadError(
                    f"DNS 解析失败（批量上传时偶发）: {str(e)}\n"
                    f"当前图表: {request_data.get('chart_name', '未知')}\n"
                    f"建议：1) 使用客户端方法Lims2Client，复用链接池，不要使用便捷函数 2) 增加重试间隔 3) 检查本地DNS配置"
                )
            raise

    def _get_content_type(self, file_format: str) -> str:
        """获取文件内容类型"""
        content_types = {
            "json": "application/json",
            "json.gz": "application/gzip",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "html": "text/html",
        }
        return content_types.get(file_format, "application/octet-stream")
