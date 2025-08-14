import argparse


def main() -> None:
    parse = argparse.ArgumentParser(
        description="Say hello to someone on the command line."
    )
    parse.add_argument(
        "names",
        nargs="+",
        help="A list of people's names. You'll say hello to them.",
    )
    parse.add_argument(
        "-s", "--shout", action="store_true", help="Yell to the mountains."
    )
    parse.add_argument(
        "-f", "--flirty", action="store_true", help="Add a little compliment."
    )

    args = parse.parse_args()

    if len(args.names) == 1:
        name_str = args.names[0]
    else:
        name_str = ", ".join(args.names[:-1]) + " and " + args.names[-1]

    message = f"Hello {name_str}"

    if args.flirty and len(args.names) == 1:
        message = message + ", you look lovely today"
    elif args.flirty:
        message = message + ", you all look lovely today"

    if args.shout:
        message = message.upper()

    print(message + "!")


if __name__ == "__main__":
    main()
