"""异常定义"""


class Lims2Error(Exception):
    """Lims2 SDK 基础异常"""

    pass


class ConfigError(Lims2Error):
    """配置错误"""

    pass


class AuthError(Lims2Error):
    """认证错误"""

    pass


class UploadError(Lims2Error):
    """上传错误"""

    pass


class APIError(Lims2Error):
    """API 调用错误"""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
