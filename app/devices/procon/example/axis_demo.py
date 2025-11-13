from __future__ import annotations

import argparse
import logging
import time

from ..controller import DigitalPoint, ProConController, ProConDllError


def ensure_axis_ready(controller: ProConController, axis: int) -> None:
    controller.clear_axis_error(axis)
    controller.power_on(axis)
    status = controller.read_axis_status(axis)
    if not bool(status.is_homed):
        logging.info("Axis %s not homed yet, starting homing sequence.", axis)
        controller.start_home(
            axis,
            mode=20,
            velocity_high=20.0,
            velocity_low=5.0,
            acceleration=200.0,
            jerk=2000.0,
            switch_move=500.0,
            probe_move=500.0,
            offset=0.0,
        )
        controller.wait_axis_done(axis, timeout=60.0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Axis diagnostics demo.")
    parser.add_argument("--axis", type=int, default=0, help="Axis index.")
    parser.add_argument("--position", type=float, default=50.0, help="Target position.")
    parser.add_argument("--velocity", type=float, default=50.0, help="Move velocity.")
    parser.add_argument("--ip", help="Optional controller IP.")
    parser.add_argument("--port", type=int, default=6000, help="Controller port.")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    controller = ProConController()
    try:
        controller.load(ip=args.ip, port=args.port)
        controller.wait_bus_ready()
        ensure_axis_ready(controller, args.axis)

        pos = controller.read_axis_position(args.axis)
        vel = controller.read_axis_velocity(args.axis)
        torque = controller.read_axis_torque(args.axis)
        status = controller.read_axis_status(args.axis)

        logging.info(
            "Axis %s current position %.4f, velocity %.4f, torque %.4f",
            args.axis,
            pos,
            vel,
            torque,
        )
        logging.info(
            "Axis status: active=%s done=%s warning=%s",
            status.active,
            status.done,
            status.axis_warn_id,
        )

        logging.info("Performing absolute move to %.2f", args.position)
        controller.move_absolute(
            args.axis,
            position=args.position,
            velocity=args.velocity,
            acceleration=200.0,
            deceleration=200.0,
        )
        time.sleep(0.5)
        logging.info(
            "Final axis position %.4f, velocity %.4f",
            controller.read_axis_position(args.axis),
            controller.read_axis_velocity(args.axis),
        )

    except ProConDllError as exc:
        logging.error("Axis demo failed: %s", exc)
        return 1
    finally:
        try:
            controller.stop_axis(args.axis)
            controller.power_off(args.axis)
        except ProConDllError:
            pass
        controller.unload()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
