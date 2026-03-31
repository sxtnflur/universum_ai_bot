from PIL import Image
from pydantic import Field
from typing_extensions import Annotated
from utils.price import process_amount
from .base import FALService


class Reve(FALService):
    price_per_one = process_amount(0.04)

    def get_price(self, **kwargs):
        return self.price_per_one * kwargs.get('num_images', 1)

    async def image_to_image(
        self,
        prompt: str,
        images: Annotated[list[Image], Field(max_length=1)],
        num_images: Annotated[int, Field(ge=1, le=4)] = 1,
    ):
        image_url = await self.upload_image(images[0])
        res = await self.request_with_polling(
            endpoint='fal-ai/reve/edit',
            arguments=dict(
                image_url=image_url,
                prompt=prompt,
                num_images=num_images,
                output_format='png'
            )
        )
        return {
            'images': [img.get('url') for img in res.get('images')],
            'price': self.get_price(num_images=num_images)
        }