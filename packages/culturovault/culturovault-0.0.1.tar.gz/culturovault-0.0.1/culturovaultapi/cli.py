import argparse
from .uploader import upload_culture
from .viewer import view_cultures

def main():
    parser = argparse.ArgumentParser(prog="culturovaultapi")
    subparsers = parser.add_subparsers(dest="command")

    # Upload command
    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("name")
    upload_parser.add_argument("by")
    upload_parser.add_argument("description")
    upload_parser.add_argument("file")
    upload_parser.add_argument("thumbnail")

    # View command
    view_parser = subparsers.add_parser("view")
    view_parser.add_argument("keyword")

    args = parser.parse_args()

    if args.command == "upload":
        upload_culture(args.name, args.by, args.description, args.file, args.thumbnail)
    elif args.command == "view":
        view_cultures(args.keyword)
    else:
        parser.print_help()
