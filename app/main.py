from fastapi import FastAPI
from app.api.router import router as api_router
from app.core.config import settings
from fastapi.responses import FileResponse
from pathlib import Path


app = FastAPI(
    title=settings.APP_NAME,
    version='1.0.0',
    debug=settings.DEBUG
)

app.include_router(
    api_router,
    prefix="/api"
)


if settings.APP_ENV.lower() == "development":
    @app.get("/dev/checkout",include_in_schema=False)
    def dev_checkout():
        checkout_file = Path(__file__).resolve().parents[1] / "razorpay-test.html"
        return FileResponse(checkout_file, media_type="text/html")