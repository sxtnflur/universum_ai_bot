

def action_type(action_type: str):
    return {
        'text-to-image': 'Текст в Фото',
        'image-to-image': 'Фото в Фото',
        'upscale-image': 'Upscale фото'
    }.get(action_type.replace('_', '-'), action_type)