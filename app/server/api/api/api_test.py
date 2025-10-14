from pathlib import Path

from starlette.responses import JSONResponse
import cv2
import numpy as np
from db import SessionLocal
from db.models import TestImage, TestGroup
from ..api_core import test_router as router
import CONFIG
from ..api_models import GroupCreate

_test_root = CONFIG.testFolder / "images"

@router.get("/test/images")
async def list_test_images():
    try:
        _test_root = CONFIG.testFolder/"images"
        items: list[str] = []
        for p in _test_root.rglob("*"):
            if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"):
                rel = p.relative_to(_test_root)
                items.append(str(rel))
        items.sort()
        return {"root": str(_test_root), "files": items}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@router.post("/test/load_image")
async def load_test_image(name: str):
    try:
        _test_root = CONFIG.testFolder/"images"
        path = (_test_root / name).resolve()
        if not str(path).startswith(str(_test_root)):
            return JSONResponse(status_code=400, content={"ok": False, "error": "invalid name"})
        if not path.exists():
            return JSONResponse(status_code=404, content={"ok": False, "error": "not found"})
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            return JSONResponse(status_code=415, content={"ok": False, "error": "unsupported image"})
        # Normalize to 3-channel uint8 BGR
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.ndim == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        if img.dtype != np.uint8:
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        return {"ok": True, "name": name}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@router.post("/test/load_default")
async def load_default():
    preferred = ["1_IMG_Texture_8Bit.png", "1_IMG_Texture_B.tif"]
    files = (await list_test_images())["files"]  # type: ignore
    choice: str | None = None
    for n in preferred:
        for f in files:
            if f.endswith("/" + n) or f == n:
                choice = f
                break
        if choice:
            break
    if not choice:
        choice = files[0] if files else None
    if not choice:
        return JSONResponse(status_code=404, content={"ok": False, "error": "no test images"})
    return await load_test_image(choice)


# Groups APIs
@router.post("/test/group/create")
async def group_create(body: GroupCreate):
    serial = body.serial.strip()
    _test_root = CONFIG.testFolder / "images"
    if not serial:
        return JSONResponse(status_code=400, content={"ok": False, "error": "serial required"})
    group_dir = (_test_root / serial)
    try:
        group_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
    db = SessionLocal()
    try:
        g = db.query(TestGroup).filter(TestGroup.serial == serial).one_or_none()
        if g is None:
            g = TestGroup(serial=serial, note=body.note)
            db.add(g)
            db.commit()
            db.refresh(g)
        else:
            if body.note and g.note != body.note:
                g.note = body.note
                db.commit()
        return {"ok": True, "serial": g.serial, "id": g.id}
    finally:
        db.close()


@router.get("/test/group/list")
async def group_list():
    db = SessionLocal()
    try:
        rows = db.query(TestGroup).order_by(TestGroup.created_at.desc()).all()
        return {
            "groups": [{"id": r.id, "serial": r.serial, "note": r.note, "created_at": r.created_at.isoformat()} for r in
                       rows]}
    finally:
        db.close()


@router.get("/test/group/{serial}/images")
async def group_images(serial: str):
    group_dir = (_test_root / serial)
    if not group_dir.exists():
        return JSONResponse(status_code=404, content={"ok": False, "error": "group folder not found"})
    files = [p.name for p in group_dir.iterdir() if
             p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")]
    files.sort()
    return {"root": str(group_dir), "files": files}


@router.post("/test/group/{serial}/add_image")
async def group_add_image(serial: str, name: str):
    src = (_test_root / name)
    if not src.exists():
        alt = Path("docs/閾滅矑瀛愰」鐩?绠楁硶/A001绮掑瓙鎵撶（/ImageSimMx") / name
        if alt.exists():
            src = alt.resolve()
    if not src.exists():
        return JSONResponse(status_code=404, content={"ok": False, "error": "source image not found"})
    dst_dir = (_test_root / serial)
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = (dst_dir / src.name)
        import shutil
        shutil.copyfile(src, dst)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
    db = SessionLocal()
    try:
        g = db.query(TestGroup).filter(TestGroup.serial == serial).one_or_none()
        if g is None:
            g = TestGroup(serial=serial)
            db.add(g)
            db.commit()
            db.refresh(g)
        rel = str(Path("娴嬭瘯鏂囦欢") / serial / src.name)
        ti = db.query(TestImage).filter(TestImage.group_id == g.id, TestImage.filename == src.name).one_or_none()
        if ti is None:
            ti = TestImage(group_id=g.id, filename=src.name, rel_path=rel)
            db.add(ti)
            db.commit()
        return {"ok": True, "file": src.name}
    finally:
        db.close()
@router.post("/test/log")
async def test_log(msg: str):
    """Append a test log message to the in-memory WS buffer.
    Useful for smoke testing `/ws/logs` without real devices.
    """
    try:
        from app.server.utils.logs import push
        push("INFO", "demo", msg)
    except Exception:
        pass
    return {"ok": True}

@router.post("/test/log/clear")
async def test_log_clear():
    """Clear in-memory log buffer (test-only)."""
    try:
        from app.server.utils.logs import get_buffer
        buf = get_buffer()
        buf.clear()
    except Exception:
        pass
    return {"ok": True}
