from fastapi import FastAPI, APIRouter

app = FastAPI(title="CopperSystem API")

image_router = APIRouter(tags=["图像服务"])
test_router = APIRouter(tags=["数据测试服务"])
motion_router = APIRouter(tags=["设备功能"])

ws_router = APIRouter(tags=["webSockets"])


app.include_router(image_router)
app.include_router(test_router)
app.include_router(motion_router)
app.include_router(ws_router)

