import sys, argparse

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

    args = parser.parse_args()

    if not sys.stdin.isatty():
        # TODO
        print("This version of ppager is not capable of using stdin :(\nIt's in TODO")
        return

    if args.file:
        Pager(text=args.file.readlines()).run()
        return

    print("Missing filename, use 'ppager --help'")


if __name__ == "__main__":
    run()
