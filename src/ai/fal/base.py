import os
from config import settings

os.environ.setdefault('FAL_KEY', settings.FAL_KEY)

import fal_client
from PIL import Image


class FALService:
    use_webhook: bool = False

    def __init__(self, webhook_base_url: str):
        self.webhook_base_url = webhook_base_url

    def get_price_description(self, func: str, kwargs: dict) -> str | None:
        return

    def get_price(self, func: str, kwargs: dict) -> float:
        ...

    async def request_with_polling(self, endpoint: str, arguments: dict,
                                   with_request_id: bool = False):
        handler = await fal_client.submit_async(endpoint, arguments=arguments)
        result = await handler.get()
        if with_request_id:
            return result, handler.request_id
        return result

    async def request_with_webhook(self, endpoint: str, arguments: dict, webhook_url: str) -> str:
        handler = await fal_client.submit_async(
            endpoint, arguments=arguments, webhook_url=webhook_url
        )
        return handler.request_id

    @staticmethod
    async def upload_file(path: str | bytes, content_type: str = 'zip'):
        return await fal_client.upload_async(path, content_type=content_type)

    @staticmethod
    async def upload_image(image: Image):
        return await fal_client.upload_image_async(image)
