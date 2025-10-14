from __future__ import annotations

import importlib
import os

import pytest


def test_root_docs_hint(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "/docs" in r.json().get("/docs", "") or "/docs" in r.text


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_image_png(client):
    r = client.get("/image.png")
    assert r.status_code == 200
    assert r.headers.get("content-type") == "image/png"
    assert len(r.content) > 0


def test_list_test_images(client):
    r = client.get("/test/images")
    assert r.status_code == 200
    data = r.json()
    assert "files" in data
    assert isinstance(data["files"], list)
    # Should include at least one known example asset
    assert any(
        name.endswith("1_IMG_Texture_8Bit.png") or name.endswith("2_IMG_Texture_8Bit.png")
        for name in data["files"]
    )


@pytest.mark.skipif(
    importlib.util.find_spec("cv2") is None, reason="cv2 not installed in test environment"
)
def test_load_default_image(client):
    r = client.post("/test/load_default")
    # When images exist, endpoint returns ok True
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        assert r.json().get("ok") is True


def test_motion_endpoints_noop_ok(client):
    # Even without a concrete motion controller, endpoints should return ok
    r1 = client.post("/motion/home")
    r2 = client.post("/motion/set_work_origin")
    assert r1.status_code == 200 and r1.json().get("ok") is True
    assert r2.status_code == 200 and r2.json().get("ok") is True
