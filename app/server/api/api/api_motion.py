import motion
from ..api_core import motion_router as router
from ..api_models import MotionSpeed, JogCmd


@router.post("/motion/set_speed")
async def motion_set_speed(body: MotionSpeed):
    if hasattr(motion, 'set_speed'):
        motion.set_speed(body.v_fast, body.v_work)
    return {"ok": True}

@router.post("/motion/jog")
async def motion_jog(body: JogCmd):
    if hasattr(motion, 'jog'):
        motion.jog(body.axis, body.direction, body.speed)
    return {"ok": True}

@router.post("/motion/home")
async def motion_home():
    if hasattr(motion, 'home'):
        motion.home()
    return {"ok": True}

@router.post("/motion/set_work_origin")
async def motion_set_work_origin():
    if hasattr(motion, 'set_work_origin'):
        motion.set_work_origin()
    return {"ok": True}