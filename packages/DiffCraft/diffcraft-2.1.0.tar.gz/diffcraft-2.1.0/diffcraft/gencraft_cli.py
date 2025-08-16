import argparse
from .generator import (
    generate_gitignore,
    generate_license,
    generate_readme,
    list_licenses
)

def main():
    """
    The main entry point for the GenCraft CLI.
    """
    parser = argparse.ArgumentParser(
        prog="gencraft",
        description="📝 GenCraft: A tool to generate essential repository files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Gitignore Command ---
    parser_gitignore = subparsers.add_parser(
        "gitignore",
        help="Generate or update a .gitignore file."
    )
    parser_gitignore.add_argument(
        'files',
        nargs='*',
        help="Optional: Additional file(s) or patterns to add to the .gitignore."
    )

    # --- License Command ---
    parser_license = subparsers.add_parser(
        "license",
        help="Generate a LICENSE file."
    )
    parser_license.add_argument(
        "license_type",
        nargs='?', # Makes the license type optional
        default=None,
        help="The type of license to generate (e.g., 'mit', 'apache-2.0')."
    )

    # --- Readme Command ---
    parser_readme = subparsers.add_parser(
        "readme",
        help="Generate a README.md file using AI."
    )
    parser_readme.add_argument(
        "prompt",
        nargs='?',
        default="A standard, well-structured README.",
        help="A short prompt describing the desired README (e.g., 'a one-paragraph readme')."
    )

    args = parser.parse_args()

    if args.command == "gitignore":
        generate_gitignore(args.files)
    elif args.command == "license":
        if not args.license_type:
            list_licenses()
        else:
            generate_license(args.license_type)
    elif args.command == "readme":
        generate_readme(args.prompt)

if __name__ == "__main__":
    main()