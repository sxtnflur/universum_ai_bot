from PIL import Image
from ai.fal.base import FALService
from ai.fal.utils import calculate_upscale_cost
from pydantic import Field
from typing_extensions import Annotated
from utils.price import process_amount


class Seedvr(FALService):
    price_per_one = process_amount(0.001)

    def get_price_description(self, func: str, kwargs: dict) -> str:
        data = calculate_upscale_cost(
            image=kwargs['images'][0],
            upscale_factor=kwargs['upscale_factor'],
            price_per_mp=self.price_per_one
        )
        return f'Цена за 1 мегапиксель: {self.price_per_one}\n' \
               f'{data["cost"]} = {round(data["megapixels"], 2)}mp x {self.price_per_one} '

    def get_price(self, func: str, kwargs: dict) -> float:
        data = calculate_upscale_cost(
            image=kwargs['images'][0],
            upscale_factor=kwargs['upscale_factor'],
            price_per_mp=self.price_per_one
        )
        return data['cost']

    async def upscale_image(
        self,
        images: Annotated[list[Image], Field(max_length=1)],
        upscale_factor: Annotated[float, Field(ge=1, le=10)] = 2,
        noise_scale: Annotated[float, Field(ge=0, le=1)] = 0.1
    ):
        image_url = await self.upload_image(images[0])
        res, request_id = await self.request_with_polling(
            endpoint='fal-ai/seedvr/upscale/image',
            arguments=dict(
                image_url=image_url,
                upscale_mode='factor',
                upscale_factor=upscale_factor,
                noise_scale=noise_scale,
                output_format='png'
            ),
            with_request_id=True
        )
        return {
            'images': [res['image']['url']],
            'request_id': request_id
        }