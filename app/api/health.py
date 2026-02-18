from fastapi import APIRouter
from typing import Dict

health_router = APIRouter(prefix="/health")


@health_router.get("/")
def get_health() -> Dict[str, str]:
    return {"status": "healthy"}
