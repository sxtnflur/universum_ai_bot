from typing_extensions import Literal

from .base import FALService


class KlingService(FALService):
    async def image_to_video(self, img_url: str, prompt: str, duration: Literal[5, 10] = 5) -> str:
        return await self.request_with_webhook(
            'fal-ai/kling-video/v1.6/pro/image-to-video',
            arguments={
                'prompt': prompt,
                'image_url': img_url,
                "duration": duration
            },
            webhook_url=f"{self.webhook_base_url}/webhook/image-to-video"
        )