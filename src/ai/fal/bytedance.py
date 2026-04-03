from PIL import Image
from pydantic import Field
from typing_extensions import Literal, Annotated
from utils.price import process_amount
from .base import FALService

RatioType = Literal['1:1', '3:4', '9:16', '4:3', '16:9']


def get_image_size(ratio: RatioType):
    return {
            '1:1': (3072, 3027),
            '3:4': (2304, 3072),
            '9:16': (1728, 3072),
            '4:3': (3072, 2304),
            '16:9': (3072, 1728)
        }[ratio]


class BytedanceSeedream5(FALService):
    price_per_one = process_amount(0.035)

    def get_price(self, func, kwargs: dict):
        return self.price_per_one * kwargs.get('num_images', 1)

    async def text_to_image(
        self,
        prompt: str,
        num_images: Annotated[int, Field(ge=1, le=6)] = 1,
        ratio: RatioType = '1:1'
    ):
        image_size = get_image_size(ratio)

        res, request_id = await self.request_with_polling(
            endpoint='fal-ai/bytedance/seedream/v5/lite/text-to-image',
            arguments=dict(
                prompt=prompt,
                image_size={
                    'width': image_size[0],
                    'height': image_size[1]
                },
                num_images=num_images,
                max_images=num_images
            ),
            with_request_id=True
        )
        return {
            'images': [img.get('url') for img in res.get('images')],
            'request_id': request_id
        }

    async def image_to_image(
        self,
        prompt: str,
        images: list[Image],
        num_images: Annotated[int, Field(ge=1, le=6)] = 1,
        ratio: RatioType = '1:1'
    ):
        image_size = get_image_size(ratio)
        image_urls = [await self.upload_image(image=image) for image in images]
        res, request_id = await self.request_with_polling(
            endpoint='fal-ai/bytedance/seedream/v5/lite/edit',
            arguments=dict(
                image_urls=image_urls,
                prompt=prompt,
                image_size={
                    'width': image_size[0],
                    'height': image_size[1]
                },
                num_images=num_images,
                max_images=num_images
            ),
            with_request_id=True
        )
        return {
            'images': [img.get('url') for img in res.get('images')],
            'request_id': request_id
        }