from PIL import Image
from pydantic import Field
from typing_extensions import Annotated
from utils.price import process_amount
from .base import FALService


class BriaFiboEdit(FALService):
    price_per_one = process_amount(0.04)

    def get_price(self, *args, **kwargs):
        return self.price_per_one

    async def image_to_image(
        self,
        prompt: str,
        images: Annotated[list[Image], Field(max_length=1)]
    ):
        image_url = await self.upload_image(images[0])
        res = await self.request_with_polling(
            endpoint='bria/fibo-edit/edit',
            arguments=dict(
                prompt=prompt,
                image_url=image_url,
                output_format='png'
            )
        )
        return {
            'images': [img['url'] for img in res['images']],
            'price': self.get_price() * len(res['images'])
        }