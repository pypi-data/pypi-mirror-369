from __future__ import annotations
import argparse, sys, pathlib
from .core import compress_file, decompress_file

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="yuac", description="YUA Compressor (custom format + AES-GCM)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("c", help="compress file")
    pc.add_argument("input", help="input file")
    pc.add_argument("-o", "--output", help="output .yuac path")
    pc.add_argument("-a", "--algo", default="zstd", choices=["store", "zlib", "zstd"], help="compression algorithm")
    pc.add_argument("-l", "--level", type=int, default=6, help="compression level (algorithm-dependent)")
    pc.add_argument("-p", "--password", help="encrypt with password (AES-GCM)")
    pc.add_argument("-y", "--yes", action="store_true", help="overwrite without prompt")

    px = sub.add_parser("x", help="extract/decompress file")
    px.add_argument("input", help=".yuac file")
    px.add_argument("-o", "--output", help="output file")
    px.add_argument("-p", "--password", help="password (if encrypted)")
    px.add_argument("-y", "--yes", action="store_true", help="overwrite without prompt")
    return p

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    p = build_parser()
    args = p.parse_args(argv)

    inp = pathlib.Path(args.input)
    if not inp.exists():
        p.error(f"input not found: {inp}")

    if args.cmd == "c":
        out = pathlib.Path(args.output) if args.output else inp.with_suffix(".yuac")
        if out.exists() and not args.yes:
            p.error(f"output exists: {out} (use -y)")
        compress_file(str(inp), str(out), algo=args.algo, level=args.level, password=args.password)
        print(f"compressed -> {out}")
    elif args.cmd == "x":
        out = pathlib.Path(args.output) if args.output else inp.with_suffix(".out")
        if out.exists() and not args.yes:
            p.error(f"output exists: {out} (use -y)")
        decompress_file(str(inp), str(out), password=args.password)
        print(f"extracted -> {out}")

if __name__ == "__main__":
    main()
