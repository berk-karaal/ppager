import sys, argparse, os

from ppager.ppager import Pager

VERSION = "0.1.1"


def run():

    parser = argparse.ArgumentParser(prog="ppager", add_help=False)

    parser.add_argument(
        "-v",
        "--version",
        default=False,
        action="version",
        version=f"%(prog)s {VERSION}",
        help="show version number of ppager",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show this help message",
    )
    parser.add_argument("file", type=argparse.FileType("r"), nargs="?")

    parser.add_argument(
        "stdin",
        type=argparse.FileType("r"),
        default=(None if sys.stdin.isatty() else sys.stdin),
        nargs="?",
    )

    args = parser.parse_args()

    if args.stdin:
        text = args.stdin.readlines()
        f = open("/dev/tty")
        os.dup2(f.fileno(), 0)

    elif args.file:
        text = args.file.readlines()
    else:
        print("Missing filename, use 'ppager --help'")
        return

    Pager(text=text).run()


if __name__ == "__main__":
    run()
