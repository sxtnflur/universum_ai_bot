from api.depends import AIUseCase
from api.schemas import FalRequest
from fastapi import APIRouter

router = APIRouter(prefix='/ai')


@router.post('/fal/images')
async def get_images(
    data: FalRequest, use_case: AIUseCase
):
    return await use_case.on_fal_request(data)