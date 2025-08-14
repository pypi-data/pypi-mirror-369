import argparse
import time

from .progress import Progress


def main():
    ap = argparse.ArgumentParser(description="Braille progress demo")
    ap.add_argument("--items", type=int, default=50)
    ap.add_argument("--force-tty", action="store_true")
    ap.add_argument("--force-color", action="store_true")
    args = ap.parse_args()

    p = Progress(force_tty=args.force_tty, force_color=args.force_color)
    with p.task("demo", total=args.items) as t:
        for i in range(args.items):
            t.advance(stage="writing", label=f"item_{i:03d}")
            time.sleep(0.02)
    p.close()
