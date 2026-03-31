from PIL import Image
from ai.fal.base import FALService
from pydantic import Field
from typing_extensions import Annotated
from utils.price import process_amount


class Recraft(FALService):
    price_per_one = process_amount(0.004)

    def get_price(self, *args, **kwargs) -> float:
        return self.price_per_one * kwargs.get('num_images', 1)

    async def upscale_image_crisp(
        self,
        images: Annotated[list[Image], Field(max_length=1)]
    ):
        image_url = await self.upload_image(images[0])
        result = await self.request_with_polling(
            endpoint='fal-ai/recraft/upscale/crisp',
            arguments=dict(
                image_url=image_url
            )
        )
        return {'images': [result['image']['url']],
                'price': self.get_price()}

    async def upscale_image_creative(
        self,
        images: Annotated[list[Image], Field(max_length=1)]
    ):
        image_url = await self.upload_image(images[0])
        result = await self.request_with_polling(
            endpoint='fal-ai/recraft/upscale/creative',
            arguments=dict(
                image_url=image_url
            )
        )
        return {'images': [result['image']['url']],
                'price': self.get_price()}
