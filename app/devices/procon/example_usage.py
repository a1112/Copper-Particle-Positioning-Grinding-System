from __future__ import annotations

import argparse
import logging

from .controller import DigitalPoint, ProConController, ProConDllError


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ProCon DLL wrapper demo matching GantryMilling capabilities.",
    )
    parser.add_argument("--ip", help="Optional controller IP address for TCP mode.")
    parser.add_argument("--port", type=int, default=6000, help="Controller TCP port.")
    parser.add_argument("--axis", type=int, default=0, help="Axis index to exercise.")
    parser.add_argument(
        "--distance", type=float, default=50.0, help="Absolute position to move to."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging output."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    controller = ProConController()
    try:
        controller.load(ip=args.ip, port=args.port)
        controller.wait_bus_ready()

        controller.clear_axis_error(args.axis)
        controller.power_on(args.axis)
        controller.move_absolute(
            args.axis,
            position=args.distance,
            velocity=50.0,
            acceleration=200.0,
            deceleration=200.0,
        )
        position = controller.read_axis_position(args.axis)
        logging.info("Axis %s actual position %.4f", args.axis, position)

        # Toggle a cylinder output as an example (0/3 placeholder).
        cylinder_out = DigitalPoint(slave_id=0, index=3)
        controller.operate_cylinder(cylinder_out, extend=True)
        logging.info("Cylinder extend command issued.")

    except ProConDllError as exc:
        logging.error("Controller error: %s", exc)
        return 1
    finally:
        try:
            controller.power_off(args.axis)
        except ProConDllError:
            pass
        controller.unload()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
