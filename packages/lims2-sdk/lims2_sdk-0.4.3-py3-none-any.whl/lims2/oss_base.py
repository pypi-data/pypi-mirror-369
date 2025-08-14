"""OSS操作基类

提取图表服务和存储服务的共同OSS操作逻辑
"""

import time
from typing import Any

import oss2

from .utils import handle_api_response


class OSSMixin:
    """OSS操作混入类

    提供STS临时凭证获取和OSS Bucket创建的通用功能
    """

    def __init_oss__(self):
        """初始化OSS混入功能"""
        # STS 凭证缓存，避免频繁请求
        self._sts_cache = {}

    def _get_oss_path_prefix(self) -> str:
        """根据API URL判断环境并返回相应的OSS路径前缀

        Returns:
            str: 环境相关的路径前缀
                - 生产环境 (api-v2): "media"
                - 测试环境 (其他): "test"
        """
        # 检查API URL是否包含"api-v2"
        is_production = "api-v2" in self.config.api_url
        return "media" if is_production else "test"

    def _get_sts_token(self, project_id: str) -> dict[str, Any]:
        """获取阿里云 STS 临时访问凭证

        Args:
            project_id: 项目 ID

        Returns:
            dict[str, Any]: STS 凭证信息，包含：
                - access_key_id: 临时访问密钥 ID
                - access_key_secret: 临时访问密钥
                - security_token: 安全令牌
                - endpoint: OSS 服务端点
                - bucket_name: OSS 存储桶名称

        Raises:
            APIError: 获取 STS 凭证失败

        Note:
            - 使用带时间戳的内存缓存避免频繁请求
            - 缓存键格式：project_id:team_id
            - STS 凭证有时效性，默认15分钟，缓存10分钟后自动刷新
            - 批量上传时能显著减少API请求次数
        """
        cache_key = f"{project_id}:{self.config.team_id}"

        # 检查缓存是否有效（包含时间检查）
        if cache_key in self._sts_cache:
            cached_data = self._sts_cache[cache_key]
            # STS凭证默认有效期15分钟，提前5分钟刷新
            if time.time() - cached_data["cache_time"] < 10 * 60:  # 10分钟内有效
                # print(f"[DEBUG] 使用缓存的STS凭证: {cache_key}")  # 可选调试信息
                return {k: v for k, v in cached_data.items() if k != "cache_time"}

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
            "cache_time": time.time(),  # 添加缓存时间戳
        }

        # 缓存凭证并返回（返回时去除时间戳）
        self._sts_cache[cache_key] = token_data
        return {k: v for k, v in token_data.items() if k != "cache_time"}

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
