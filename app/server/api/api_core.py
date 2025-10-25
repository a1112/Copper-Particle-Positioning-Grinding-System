from fastapi import FastAPI, APIRouter

from app.server.httpbridge.routes import bridge_router

app = FastAPI(title="CopperSystem API")

image_router = APIRouter(tags=["images"])
test_router = APIRouter(tags=["tests"])
motion_router = APIRouter(tags=["motion"])
status_router = APIRouter(tags=["status"])
ws_router = APIRouter(tags=["websockets"])
control_router = APIRouter(tags=["control"])
config_router = APIRouter(tags=["config"])
path_router = APIRouter(tags=["path"])
cutting_router = APIRouter(tags=["cutting"])
tool_router = APIRouter(tags=["tool"])
vision_router = APIRouter(tags=["vision"])
data_router = APIRouter(tags=["data"])


def include_router():
    app.include_router(bridge_router)
    app.include_router(image_router)
    app.include_router(test_router)
    app.include_router(motion_router)
    app.include_router(ws_router)
    app.include_router(status_router)
    app.include_router(control_router)
    app.include_router(config_router)
    app.include_router(cutting_router)
    app.include_router(path_router)
    app.include_router(tool_router)
    app.include_router(vision_router)
    app.include_router(data_router)
