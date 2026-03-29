import dataclasses
from mytypes import ActionType


@dataclasses.dataclass
class Model:
    key: str
    title: str
    types: list[ActionType | tuple[str, str]]


models = {
    'nano_banana': Model(
        key='nano_banana',
        title='Nano Banana',
        types=['text_to_image', 'image_to_image']
    ),
    'nano_banana_pro': Model(
            key='nano_banana_pro',
            title='Nano Banana Pro',
            types=['text_to_image', 'image_to_image']
        ),
    'nano_banana_2': Model(
        key='nano_banana_2',
        title='Nano Banana 2',
        types=['text_to_image', 'image_to_image']
    ),
    'bytesdance_seedream_5': Model(
        key='bytesdance_seedream_5',
        title='Seedream v5',
        types=['text_to_image', 'image_to_image']
    ),
    'phota': Model(
        key='phota',
        title='Phota',
        types=['text_to_image', 'image_to_image']
    ),
    'reve': Model(
        key='reve',
        title='Reve',
        types=['image_to_image']
    ),
    'bria_fibo_edit': Model(
        key='bria_fibo_edit',
        title='Fibo-Edit',
        types=['image_to_image']
    ),
    'recraft': Model(
        key='recraft',
        title='Recraft',
        types=[('upscale_image_crisp', 'Upscale Фото (Crisp)'),
               ('upscale_image_creative', 'Upscale Фото (Creative)')]
    ),
    'seedvr': Model(
        key='seedvr',
        title='SeedVR',
        types=['upscale_image']
    )
}