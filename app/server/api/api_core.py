from fastapi import FastAPI, APIRouter

app = FastAPI(title="CopperSystem API")

image_router = APIRouter(tags=["图像服务"])
test_router = APIRouter(tags=["数据测试服务"])
motion_router = APIRouter(tags=["设备功能"])

app.include_router(image_router)
app.include_router(test_router)
app.include_router(motion_router)

@app.get("/")
def read_root():
    return {"/docs": "请访问 /docs 查看文档"}

@app.get("/delay")
async def get_delay():
    return 0

@app.get("/health")
async def health():
    return {"status": "ok"}