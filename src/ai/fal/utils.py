from PIL import Image


def calculate_upscale_cost(image: Image, upscale_factor, price_per_mp=0.001):
    # открываем изображение
    width, height = image.size

    # новое разрешение
    new_width = width * upscale_factor
    new_height = height * upscale_factor

    # мегапиксели после апскейла
    megapixels = (new_width * new_height) / 1_000_000

    # стоимость
    cost = megapixels * price_per_mp

    return {
        "original_size": (width, height),
        "upscaled_size": (new_width, new_height),
        "megapixels": megapixels,
        "cost": round(cost, 2)
    }