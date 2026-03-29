from .start import router as start_router
from .models import router as models_router
from .payment import router as payment_router
from .unhandled import router as unhandled_router
from .support import router as support_router


__routers__ = (
    start_router,
    support_router,
    payment_router,
    models_router,
    unhandled_router
)