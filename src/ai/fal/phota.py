from PIL import Image
from pydantic import Field
from typing_extensions import Literal, Annotated
from utils.price import process_amount
from .base import FALService


class Phota(FALService):
    price_per_one = process_amount(0.09)

    def get_price_description(self, *args, **kwargs) -> str:
        return f'За одно изображение с качеством 1K цена {self.price_per_one}, ' \
               f'за 4К - удвоенная цена ({self.price_per_one*2})'

    def get_price(self, func: str, kwargs: dict):
        price = self.price_per_one
        if kwargs.get('resolution') == '4K':
            price *= 2
        return round(price * kwargs.get('num_images', 1), 2)

    async def text_to_image(
        self,
        prompt: str,
        num_images: Annotated[int, Field(ge=1, le=4)] = 1,
        resolution: Literal['1K', '4K'] = '1K',
        ratio: Literal['auto', '1:1', '16:9', '4:3',
                              '3:4', '9:16'] = 'auto',
        # profile_ids: list[str] | None = None
    ):
        args = dict(
            prompt=prompt,
            num_images=num_images,
            resolution=resolution,
            aspect_ratio=ratio,
            output_format='png'
        )
        res, request_id = await self.request_with_polling(
            endpoint='fal-ai/phota',
            arguments=args,
            with_request_id=True
        )
        return {
            'images': [img.get('url') for img in res.get('images')],
            'price': self.get_price(
                func='text_to_image', kwargs=args
            ),
            'request_id': request_id
        }

    async def image_to_image(
        self,
        prompt: str,
        images: Annotated[list[Image], Field(max_length=10)],
        num_images: Annotated[int, Field(ge=1, le=4)] = 1,
        resolution: Literal['1K', '4K'] = '1K',
        ratio: Literal['auto', '1:1', '16:9', '4:3',
                              '3:4', '9:16'] = 'auto',
    ):
        image_urls = [await self.upload_image(image=image) for image in images]
        args = dict(
                prompt=prompt,
                image_urls=image_urls,
                num_images=num_images,
                resolution=resolution,
                aspect_ratio=ratio,
                output_format='png'
            )
        res, request_id = await self.request_with_polling(
            endpoint='fal-ai/phota/edit',
            arguments=args,
            with_request_id=True
        )
        return {
            'images': [img.get('url') for img in res.get('images')],
            'price': self.get_price(
                func='text_to_image', kwargs=args
            ),
            'request_id': request_id
        }