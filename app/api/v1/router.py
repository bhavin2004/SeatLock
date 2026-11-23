from fastapi import APIRouter
from app.modules.health.router import router as health_router
from app.modules.movies.router import router as movies_router
from app.modules.auth.router import router as auth_router
from app.modules.bookings.router import router as bookings_router
from app.modules.shows.router import router as shows_router
from app.modules.theaters.router import router as theaters_router
from app.modules.screens.router import router as screens_router
from app.modules.payments.router import router as webhooks_router



router = APIRouter()

router.include_router(auth_router)

router.include_router(health_router)

router.include_router(movies_router)

router.include_router(bookings_router)

router.include_router(shows_router)

router.include_router(theaters_router)

router.include_router(screens_router)

router.include_router(webhooks_router)