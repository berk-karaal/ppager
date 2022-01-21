import sys, os

from ppager.ppager import Pager


def run():

    VERSION = "0.1.1"
    argv = sys.argv

    pager_should_run = False

    if not sys.stdin.isatty():
        # TODO
        print("This version of ppager is not capable of using stdin :(\nIt's in TODO")

    else:
        if len(argv) == 2:
            if argv[1] in ["-V", "--version"]:
                print(f"ppager {VERSION}")

            elif argv[1] in ["-H", "--help"]:
                print(
                    "ppager is PAGER like less command in UNIX systems. It was mainly developed as a Python library that programmers can implement it to their projects.\nIn order to use ppager in command line:\n\nppager\n"
                    + "-v --version  : ppager version\n"
                    + "-h --help     : display this help menu\n"
                    + "<document>    : display given document\n"
                )

            else:
                try:
                    with open(os.getcwd() + "/" + argv[1]) as file:
                        text = file.read().splitlines()
                    pager_should_run = True

                except FileNotFoundError:
                    print(f"'{argv[1]}' couldn't be found")

                except IsADirectoryError:
                    print(f"'{argv[1]}' is a directory")

        elif len(argv) == 1:
            print('Missing filename ("ppager --help" for help)')

        else:
            print('Unknown input ("ppager --help" for help)')

    if pager_should_run:
        p = Pager(text=text)
        p.run()


if __name__ == "__main__":
    run()
