from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    FAL_KEY: str
    BOT_TOKEN: str
    BOT_USERNAME: str
    DATABASE_URL: str
    YOOKASSA_SHOP_ID: int
    YOOKASSA_API_KEY: str

    SUPPORT_URL: str = '@teledeff_support'

    MIN_AMOUNT_UP_BALANCE: float = 1

    @property
    def BOT_URL(self):
        return f'https://t.me/{self.BOT_USERNAME}'


settings = Settings(_env_file='.env')