import argparse
from .main import run

def main():
    """
    The main entry point for the DiffCraft CLI.
    """
    epilog_text = """
Examples:
  craft
      Generate a commit message interactively.

  craft -t fix -e
      Generate a 'fix' type commit and open it directly in your editor.

  craft --lang Spanish --history 3
      Generate a message in Spanish using the last 3 commits as context.

Find more information or contribute at the project repository.
"""

    parser = argparse.ArgumentParser(
        prog="craft",
        description="🚀 DiffCraft: Your AI-powered git commit assistant.",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    gen_group = parser.add_argument_group('Generation Options')
    flow_group = parser.add_argument_group('Workflow Options')

    gen_group.add_argument(
        '-t', '--type',
        type=str,
        choices=['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore'],
        help="Specify the commit type. If omitted, the AI will auto-detect."
    )

    gen_group.add_argument(
        '--lang',
        type=str,
        default='English',
        metavar='LANGUAGE',
        help="Set the output language for the message (e.g., 'Spanish', 'Japanese')."
    )

    flow_group.add_argument(
        '-e', '--edit',
        action='store_true',
        help="Bypass the interactive prompt and open the message directly in your editor."
    )

    flow_group.add_argument(
        '--history',
        type=int,
        default=0,
        metavar='N',
        help="Provide the last N commit messages to the AI for better context."
    )

    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()