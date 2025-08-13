import sys

from tamm._cli.common import HEADER, get_extended_root_parser


def main(args=None):
    parser = get_extended_root_parser()

    args = args if args is not None else sys.argv[1:]
    if len(args) == 0:
        print(HEADER)
        parser.print_help()
        return

    parsed_args = parser.parse_args(args)
    kwargs = vars(parsed_args)
    kwargs = {k.replace("-", "_"): v for k, v in kwargs.items()}
    if "func" in kwargs:
        func = kwargs.pop("func")
        func(**kwargs)
    else:
        parser.parse_args([*args, "--help"])


if __name__ == "__main__":
    main()
