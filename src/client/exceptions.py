from src.client.schemas import Captcha


class InvalidCaptcha(Exception):
    """Если нужна капча для запроса, используем эту ошибочку"""

    def __init__(self, message: str, captcha: Captcha):
        super().__init__(message)

        self.captcha = captcha
