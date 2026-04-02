from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    FAL_KEY: str
    BOT_TOKEN: str
    BOT_USERNAME: str
    DATABASE_URL: str
    YOOKASSA_SHOP_ID: int
    YOOKASSA_API_KEY: str

    API_PREFIX: str = '/universumai/api/v1'
    BOT_WEBHOOK_ENDPOINT: str = '/webhook'
    BOT_WEBHOOK_URL: str

    SUPPORT_URL: str = '@teledeff_support'

    MIN_AMOUNT_UP_BALANCE: float = 1

    ADMIN_IDS: list[int] = [1304563494]

    SECRET_TOKEN: str

    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str
    S3_BUCKET: str

    @property
    def BOT_URL(self):
        return f'https://t.me/{self.BOT_USERNAME}'


settings = Settings(_env_file='.env')