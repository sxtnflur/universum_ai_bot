from .base import BaseRepo
from .. import models


class PaymentsRepo(BaseRepo[models.Payment]):
    model = models.Payment