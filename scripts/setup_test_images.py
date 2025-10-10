from __future__ import annotations

from pathlib import Path
import shutil


def main() -> None:
    """准备测试图片（中文注释）

    从示例目录复制若干图片到 测试文件/demo-0001/，便于快速联调。
    """
    repo = Path(__file__).resolve().parents[1]
    # Create a demo group folder under 测试文件/<serial>
    dst_dir = repo / "测试文件" / "demo-0001"
    dst_dir.mkdir(parents=True, exist_ok=True)
    candidates = [
        repo / "docs/铜粒子项目/算法/A001粒子打磨/ImageSimMx/1_IMG_Texture_8Bit.png",
        repo / "docs/铜粒子项目/算法/A001粒子打磨/ImageSimMx/2_IMG_Texture_8Bit.png",
    ]
    copied = []
    for src in candidates:
        if src.exists():
            dst = dst_dir / src.name
            if not dst.exists():
                shutil.copyfile(src, dst)
                copied.append(dst)
    print("created:")
    for p in copied:
        print(p)


if __name__ == "__main__":
    main()
