import dataclasses
from typing import Callable, get_origin, get_args, Annotated, Literal
import inspect

from annotated_types import MaxLen, MinLen, Ge, Le
from pydantic import Field


@dataclasses.dataclass
class GenFuncInfo:
    func: str
    arguments: dict | None = None
    required_arguments: dict[str, inspect.Parameter] | None = None

    min_input_num_images: int | None = None
    max_input_num_images: int | None = None

    min_images: int | None = None
    max_images: int | None = None

    additional_arguments: dict[str, inspect.Parameter] | None = None


def inspect_generation_func(func: Callable):
    f = inspect.signature(func)

    args = {}
    req_args = {}
    additional_args = {}

    for k, v in f.parameters.items():
        if v.default == inspect.Parameter.empty:
            req_args[k] = v
        else:
            additional_args[k] = v
        args[k] = v

    min_input_num_images = 1
    max_input_num_images = 1
    max_count_images = None
    min_count_images = None

    if 'num_images' in args and get_origin(args['num_images'].annotation) == Annotated:
        for p in get_args(args['num_images'].annotation)[1].metadata:
            if isinstance(p, Ge):
                min_input_num_images = p.ge
            elif isinstance(p, Le):
                max_input_num_images = p.le

    if 'images' in req_args:
        if (
            get_origin(req_args['images'].annotation) == Annotated
        ):
            for p in get_args(req_args['images'].annotation)[1].metadata:
                if isinstance(p, MaxLen):
                    max_count_images = p.max_length
                elif isinstance(p, MinLen):
                    min_count_images = p.min_length
        return GenFuncInfo(
            func=func.__name__,
            arguments=args,
            required_arguments=req_args,
            min_input_num_images=min_input_num_images,
            max_input_num_images=max_input_num_images,
            min_images=min_count_images,
            max_images=max_count_images,
            additional_arguments=additional_args
        )
    elif 'prompt' in req_args:
        return GenFuncInfo(
            func=func.__name__,
            arguments=args,
            required_arguments=req_args,
            min_input_num_images=min_input_num_images,
            max_input_num_images=max_input_num_images,
            additional_arguments=additional_args
        )