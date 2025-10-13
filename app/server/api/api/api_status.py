from ..api_core import status_router as router


@router.get("/status")
async def status():
    pos = motion.status() if hasattr(motion, 'status') else (0, 0, 0, 0)
    st = getattr(orch.sm, 'state', None)
    state = st.name if st else 'UNKNOWN'
    if spindle:
        try:
            rpm = float(spindle.rpm_actual())
        except Exception:
            rpm = 0.0
        base_torque = max(0.0, min(2.0, rpm / 6000.0 * 1.2))
        torque = base_torque + (random.random() - 0.5) * 0.05
    else:
        t = time.monotonic() - _sim_t0
        rpm = 1500.0 + 600.0 * math.sin(2.0 * math.pi * 0.15 * t) + 120.0 * math.sin(2.0 * math.pi * 1.1 * t)
        torque = 0.6 + 0.25 * math.sin(2.0 * math.pi * 0.22 * t + 1.3) + 0.04 * math.sin(2.0 * math.pi * 1.8 * t)
        rpm = max(0.0, rpm)
        torque = max(0.0, torque)
    from app.server.CONFIG import DEBUG as _DBG
    return {
        "state": state,
        "position": {"x": pos[0], "y": pos[1], "z": pos[2], "theta": pos[3]},
        "spindle_rpm": int(rpm),
        "spindle_torque": round(torque, 3),
        "seriesA": rpm,
        "seriesB": torque,
        "debug": bool(_DBG),  }# Test images support】

@router.get("/")
def read_root():
    return {"/docs": "请访问 /docs 查看文档"}

@router.get("/delay")
async def get_delay():
    return 0

@router.get("/health")
async def health():
    return {"status": "ok"}