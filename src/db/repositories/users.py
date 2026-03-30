from sqlalchemy import select, func
from .base import BaseRepo
from .. import models


class UsersRepo(BaseRepo[models.User]):
    model = models.User

    async def get_utm_stats(self, **filters) -> list[tuple[str, int]]:
        stmt = (
            select(
                self.model.utm,
                func.count(self.model.id).label("count")
            )
            .filter(*self._prepare_filters(filters))
            .group_by(self.model.utm)
            .order_by(func.count(self.model.id).desc())
        )
        res = await self.db.execute(stmt)
        return res.all()