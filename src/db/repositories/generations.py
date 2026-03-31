from .base import BaseRepo
from .. import models


class GenerationRequestsRepo(BaseRepo[models.GenerationRequest]):
    model = models.GenerationRequest
