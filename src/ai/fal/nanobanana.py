from PIL.Image import Image
from pydantic import Field
from typing_extensions import Literal, Annotated
from utils.price import process_amount

from .base import FALService

RatioType = Literal['auto', '1:1', '3:4', '9:16', '16:9']
Version = Literal['nano-banana', 'nano-banana-pro', 'nano-banana-2']
Resolution = Literal['0.5K', '1K', '2K', '4K']
ThinkingLevel = Literal['minimal', 'high']


class GeneralNanoBananaService:
    def __init__(self, fal: FALService):
        self.fal = fal

    async def text_to_image(
        self,
        prompt: str,
        num_images: int,
        resolution: Resolution | None = None,
        version: Version = 'nano-banana-2',
        ratio: RatioType | None = None,
        limit_generations: int | None = None,
        thinking_level: ThinkingLevel | None = None
    ):
        if version not in ('nano-banana', 'nano-banana-pro', 'nano-banana-2'):
            raise

        args = {
            'prompt': prompt,
            'num_images': num_images,
            'output_format': 'png'
        }

        if resolution:
            args.update(resolution=resolution)
        if ratio:
            args.update(aspect_ratio=ratio)
        if limit_generations:
            args.update(limit_generations=limit_generations)
        if thinking_level:
            args.update(thinking_level=thinking_level)

        res = await self.fal.request_with_polling(
            f'fal-ai/{version}', arguments=args
        )
        res_images = [image.get('url') for image in res.get('images')]
        return {
            'images': res_images,
            'text': res.get('description'),
            'price': self.fal.get_price(
                func='text_to_image',
                kwargs=args
            ) * len(res['images'])
        }

    async def image_to_image(
            self,
            prompt: str,
            images: list[Image],
            num_images: int,
            resolution: Resolution | None = None,
            version: Version = 'nano-banana-2',
            ratio: RatioType | None = None,
            thinking_level: ThinkingLevel | None = None
    ) -> dict:
        if version not in ('nano-banana', 'nano-banana-pro', 'nano-banana-2'):
            raise

        image_urls = [await self.fal.upload_image(image=image) for image in images]
        args = {
            'prompt': prompt,
            'image_urls': image_urls,
            'num_images': num_images
        }
        if resolution:
            args.update(resolution=resolution)
        if ratio:
            args.update(aspect_ratio=ratio)
        if thinking_level:
            args.update(thinking_level=thinking_level)
        res = await self.fal.request_with_polling(
            f'fal-ai/{version}/edit', arguments=args
        )
        res_images = [image.get('url') for image in res.get('images')]
        return {
            'images': res_images,
            'description': res.get('text'),
            'price': self.fal.get_price(
                func='image_to_image',
                kwargs=args
            )
        }


class NanoBanana(FALService):
    price_per_one = process_amount(0.039)

    def get_price(self, **kwargs):
        return self.price_per_one * kwargs.get('num_images', 1)

    async def text_to_image(
            self,
            prompt: str,
            num_images: Annotated[int, Field(ge=1, le=4)] = 1,
            ratio: Literal['1:1', '3:4', '9:16', '16:9'] = '1:1'
    ):
        return await GeneralNanoBananaService(self).text_to_image(
            prompt=prompt,
            num_images=num_images,
            version='nano-banana',
            ratio=ratio,
            resolution=None
        )

    async def image_to_image(
            self,
            prompt: str,
            images: Annotated[list[Image], Field(max_length=4)],
            num_images: Annotated[int, Field(ge=1, le=4)] = 1,
            ratio: RatioType = 'auto'
    ) -> dict:
        return await GeneralNanoBananaService(self).image_to_image(
            prompt=prompt,
            images=images,
            num_images=num_images,
            version='nano-banana',
            ratio=ratio,
            resolution=None
        )


class NanoBananaPro(FALService):
    price_per_one = process_amount(0.15)

    def get_price_description(self, *args, **kwargs) -> str:
        return f'За одно изображение с качеством 1K или 2K - {self.price_per_one}, ' \
               f'за 4К - удвоенная цена ({self.price_per_one*2})'

    def get_price(self, func: str, kwargs: dict) -> float:
        price = self.price_per_one
        if kwargs.get('resolution') == '4K':
            price *= 2
        return round(price * kwargs.get('num_images', 1), 2)

    async def text_to_image(
            self,
            prompt: str,
            num_images: Annotated[int, Field(ge=1, le=4)] = 1,
            resolution: Literal['1K', '2K', '4K'] = '1K',
            ratio: RatioType = '1:1'
    ):
        return await GeneralNanoBananaService(self).text_to_image(
            prompt=prompt,
            num_images=num_images,
            version='nano-banana-pro',
            ratio=ratio,
            resolution=resolution
        )

    async def image_to_image(
            self,
            prompt: str,
            images: Annotated[list[Image], Field(max_length=4)],
            num_images: Annotated[int, Field(ge=1, le=4)] = 1,
            resolution: Resolution = '1K',
            ratio: RatioType = 'auto'
    ) -> dict:
        return await GeneralNanoBananaService(self).image_to_image(
            prompt=prompt,
            images=images,
            num_images=num_images,
            version='nano-banana-pro',
            ratio=ratio,
            resolution=resolution
        )


class NanoBanana2(FALService):
    price_per_one = process_amount(0.08)

    def get_price_description(self, *args, **kwargs) -> str:
        return f'За одно изображение с качеством 1K - {self.price_per_one}, ' \
               f'2K - {self.price_per_one*1.5}, 4K - {self.price_per_one*2}, 0.5K - {self.price_per_one*0.75}'

    def get_price(self, func: str, kwargs: dict):
        price = self.price_per_one
        if kwargs.get('resolution') == '4K':
            price *= 2
        elif kwargs.get('resolution') == '2K':
            price *= 1.5
        elif kwargs.get('resolution') == '0.5K':
            price *= 0.75

        if kwargs.get('thinking_level') == 'high':
            price += 0.01
        return round(price * kwargs.get('num_images', 1), 2)

    async def text_to_image(
            self,
            prompt: str,
            num_images: Annotated[int, Field(ge=1, le=4)] = 1,
            resolution: Resolution = '1K',
            ratio: RatioType = 'auto',
            thinking_level: ThinkingLevel = 'minimal'
    ):
        return await GeneralNanoBananaService(self).text_to_image(
            prompt=prompt,
            num_images=num_images,
            version='nano-banana-2',
            ratio=ratio,
            resolution=resolution,
            thinking_level=thinking_level
        )

    async def image_to_image(
            self,
            prompt: str,
            images: Annotated[list[Image], Field(max_length=4)],
            num_images: Annotated[int, Field(ge=1, le=4)] = 1,
            resolution: Resolution = '1K',
            ratio: RatioType = 'auto',
            thinking_level: ThinkingLevel = 'minimal'
    ) -> dict:
        return await GeneralNanoBananaService(self).image_to_image(
            prompt=prompt,
            images=images,
            num_images=num_images,
            version='nano-banana-2',
            ratio=ratio,
            resolution=resolution,
            thinking_level=thinking_level
        )