from typing_extensions import Literal
from .bria import BriaFiboEdit
from .nanobanana import NanoBanana, NanoBananaPro, NanoBanana2
from .bytedance import BytedanceSeedream5
from .base import FALService
from .phota import Phota
from .recraft import Recraft
from .reve import Reve
from .seedvr import Seedvr

ModelsKeys = Literal['nano-banana', 'nano-banana-pro', 'nano-banana-2',
                    'bytes-dance_seedream_5',
                    'photo', 'reve', 'bria_fibo_edit']


class FalFactory:
    def __init__(self, webhook_base_url: str):
        self.webhook_base_url = webhook_base_url

    def get_model_by_key(self, key: ModelsKeys) -> FALService:
        return getattr(self, key.replace('-', '_'))

    @property
    def nano_banana(self):
        return NanoBanana(self.webhook_base_url)

    @property
    def nano_banana_pro(self):
        return NanoBananaPro(self.webhook_base_url)

    @property
    def nano_banana_2(self):
        return NanoBanana2(self.webhook_base_url)

    @property
    def bytesdance_seedream_5(self):
        return BytedanceSeedream5(self.webhook_base_url)

    @property
    def phota(self):
        return Phota(self.webhook_base_url)

    @property
    def reve(self):
        return Reve(self.webhook_base_url)

    @property
    def bria_fibo_edit(self):
        return BriaFiboEdit(self.webhook_base_url)

    @property
    def recraft(self):
        return Recraft(self.webhook_base_url)

    @property
    def seedvr(self):
        return Seedvr(self.webhook_base_url)