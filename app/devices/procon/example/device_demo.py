from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict

from controller import DigitalPoint, ProConController, ProConDllError


def parse_point(value: str) -> DigitalPoint:
    try:
        slave_str, index_str = value.split(":")
        return DigitalPoint(slave_id=int(slave_str), index=int(index_str))
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid digital point '{value}', expected <slave>:<index>."
        ) from exc


def status_command(controller: ProConController, args: argparse.Namespace) -> None:
    controller.wait_bus_ready()
    controller.clear_axis_error(args.axis)
    pos = controller.read_axis_position(args.axis)
    vel = controller.read_axis_velocity(args.axis)
    torque = controller.read_axis_torque(args.axis)
    status = controller.read_axis_status(args.axis)

    payload: dict[str, object] = {
        "axis": args.axis,
        "position": pos,
        "velocity": vel,
        "torque": torque,
        "status": {
            "active": int(status.active),
            "done": int(status.done),
            "is_homed": int(status.is_homed),
            "warnning": int(status.warnning),
            "axis_warn_id": int(status.axis_warn_id),
            "drv_error_id": int(status.drv_error_id),
            "power_on": int(status.power_on),
        },
    }

    if args.temperature is not None:
        main_idx, sub_idx = args.temperature
        try:
            value = controller.read_pdo_object(
                controller.module.YKE_NODE.YKE_ECAT_A.value,
                args.axis,
                main_idx,
                sub_idx,
                size=args.temperature_size,
                signed=args.temperature_signed,
            )
            payload["temperature"] = value
        except ProConDllError as exc:
            logging.warning("Temperature read failed: %s", exc)

    print(json.dumps(payload, indent=2))


def move_command(controller: ProConController, args: argparse.Namespace) -> None:
    controller.wait_bus_ready()
    controller.clear_axis_error(args.axis)
    controller.power_on(args.axis)
    controller.move_absolute(
        args.axis,
        position=args.position,
        velocity=args.velocity,
        acceleration=args.acceleration,
        deceleration=args.deceleration,
        jerk_acc=args.jerk,
        jerk_dec=args.jerk,
    )
    logging.info(
        "Move complete, axis %s at %.4f",
        args.axis,
        controller.read_axis_position(args.axis),
    )


def velocity_command(controller: ProConController, args: argparse.Namespace) -> None:
    controller.wait_bus_ready()
    controller.clear_axis_error(args.axis)
    controller.power_on(args.axis)
    controller.move_velocity_ex(
        args.axis,
        velocity=args.velocity,
        acceleration=args.acceleration,
        deceleration=args.deceleration,
        jerk_acc=args.jerk,
        jerk_dec=args.jerk,
    )
    logging.info("Axis %s velocity command issued.", args.axis)


def cylinder_get(controller: ProConController, args: argparse.Namespace) -> None:
    state = controller.read_digital_output(args.output)
    payload = {"output": f"{args.output.slave_id}:{args.output.index}", "state": int(state)}
    if args.feedback:
        payload["feedback"] = int(controller.read_digital_input(args.feedback))
    print(json.dumps(payload, indent=2))


def cylinder_set(controller: ProConController, args: argparse.Namespace) -> None:
    controller.write_digital_output(args.output, args.state)
    logging.info(
        "Cylinder output %s:%s set to %s",
        args.output.slave_id,
        args.output.index,
        args.state,
    )
    if args.feedback:
        controller.wait_digital_input(
            args.feedback,
            state=args.state,
            timeout=args.timeout,
            poll_interval=args.poll_interval,
        )
        logging.info("Feedback %s:%s reached state %s", args.feedback.slave_id, args.feedback.index, args.state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ProCon device demo using the controller wrapper.",
    )
    parser.add_argument("--ip", help="Optional controller IP.")
    parser.add_argument("--port", type=int, default=6000, help="Controller port.")
    parser.add_argument("--log-level", default="INFO", help="Logging level.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Fetch axis status/telemetry.")
    status.add_argument("--axis", type=int, default=0, help="Axis index.")
    status.add_argument(
        "--temperature",
        type=lambda x: tuple(int(part, 0) for part in x.split(":")),
        help="Optional PDO main:sub index for temperature (e.g. 0x2324:1).",
    )
    status.add_argument("--temperature-size", type=int, default=2)
    status.add_argument("--temperature-signed", action="store_true", help="Decode temperature as signed integer.")

    move = subparsers.add_parser("move", help="Absolute positioning move.")
    move.add_argument("--axis", type=int, default=0)
    move.add_argument("--position", type=float, required=True)
    move.add_argument("--velocity", type=float, default=50.0)
    move.add_argument("--acceleration", type=float, default=200.0)
    move.add_argument("--deceleration", type=float, default=200.0)
    move.add_argument("--jerk", type=float, default=2000.0)

    velocity = subparsers.add_parser("velocity", help="Velocity mode command.")
    velocity.add_argument("--axis", type=int, default=0)
    velocity.add_argument("--velocity", type=float, required=True)
    velocity.add_argument("--acceleration", type=float, default=200.0)
    velocity.add_argument("--deceleration", type=float, default=200.0)
    velocity.add_argument("--jerk", type=float, default=2000.0)

    cyl_get = subparsers.add_parser("cylinder-get", help="Read cylinder output/feedback.")
    cyl_get.add_argument("--output", type=parse_point, required=True)
    cyl_get.add_argument("--feedback", type=parse_point)

    cyl_set = subparsers.add_parser("cylinder-set", help="Set cylinder output and wait for feedback.")
    cyl_set.add_argument("--output", type=parse_point, required=True)
    cyl_set.add_argument("--state", type=lambda x: bool(int(x)), required=True)
    cyl_set.add_argument("--feedback", type=parse_point)
    cyl_set.add_argument("--timeout", type=float, default=5.0)
    cyl_set.add_argument("--poll-interval", type=float, default=0.02)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    controller = ProConController()
    try:
        controller.load(ip=args.ip, port=args.port)

        if args.command == "status":
            status_command(controller, args)
        elif args.command == "move":
            move_command(controller, args)
        elif args.command == "velocity":
            velocity_command(controller, args)
        elif args.command == "cylinder-get":
            cylinder_get(controller, args)
        elif args.command == "cylinder-set":
            cylinder_set(controller, args)
        else:
            parser.error(f"Unknown command {args.command}")
    except ProConDllError as exc:
        logging.error("Operation failed: %s", exc)
        return 1
    finally:
        try:
            if args.command in {"move", "velocity"}:
                controller.stop_axis(getattr(args, "axis", 0))
                controller.power_off(getattr(args, "axis", 0))
        except ProConDllError:
            pass
        controller.unload()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
