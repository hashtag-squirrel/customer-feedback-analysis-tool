from fastapi import APIRouter

health_router = APIRouter(prefix="/health")


@health_router.get("/")
def get_health() -> dict[str, str]:
    return {"status": "healthy"}
