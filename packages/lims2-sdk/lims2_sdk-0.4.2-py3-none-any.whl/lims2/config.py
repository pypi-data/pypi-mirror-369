"""配置管理模块"""

import os
from typing import Dict, Optional


class Config:
    """配置管理类"""

    def __init__(self, api_url: Optional[str] = None, token: Optional[str] = None):
        """初始化配置

        Args:
            api_url: API 地址，如果不提供则从环境变量读取
            token: API Token，如果不提供则从环境变量读取
        """
        self.api_url = (
            api_url
            if api_url is not None
            else os.environ.get("LIMS2_API_URL") or "https://api-v1.lims2.com"
        )
        self.token = token or os.environ.get("LIMS2_API_TOKEN")
        self.team_id = (
            os.environ.get("LIMS2_TEAM_ID") or "be4e0714c336d2b4bfe00718310d01d5"
        )

        self.timeout = 600  # 默认10分钟

        # OSS配置
        self.oss_endpoint = (
            os.environ.get("LIMS2_OSS_ENDPOINT") or "oss-cn-shanghai.aliyuncs.com"
        )
        self.oss_bucket_name = os.environ.get("LIMS2_OSS_BUCKET_NAME") or "protree"

    def validate(self) -> None:
        """验证配置是否完整"""
        if not self.api_url:
            raise ValueError("API URL 未配置，请设置环境变量 LIMS2_API_URL")
        if not self.token:
            raise ValueError("API Token 未配置，请设置环境变量 LIMS2_API_TOKEN")

    def get_headers(self) -> Dict[str, str]:
        """获取 API 请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
