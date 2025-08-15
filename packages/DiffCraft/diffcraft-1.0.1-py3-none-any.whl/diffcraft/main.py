import sys
from .git_utils import get_staged_diff, commit, get_commit_history, add_files
from .ai_client import generate_commit_message
from .editor import open_in_editor

def get_user_choice():
    """Prompts the user for their choice and returns it."""
    while True:
        choice = input("Accept, Edit, Regenerate, or Quit? [A/E/R/Q]: ").upper()
        if choice in ['A', 'E', 'R', 'Q']:
            return choice
        print("Invalid choice. Please enter 'A', 'E', 'R', or 'Q'.")

def run(args):
    """
    Main function to run the commit message generation and interaction process.
    """
    # If file paths are provided as arguments, stage them first.
    if args.files:
        add_files(args.files)

    # Get the diff of all currently staged changes.
    diff = get_staged_diff()
    if not diff:
        print("No changes to commit. Use 'craft .' or 'git add <files>' to stage changes.")
        sys.exit(0)

    # Get commit history if requested by the user.
    commit_history = get_commit_history(args.history)

    commit_message = None
    is_editing_flow = args.edit

    while True:
        if not commit_message:
            print("⏳ Generating commit message with AI...")
            commit_message = generate_commit_message(
                diff,
                commit_type=args.type,
                history=commit_history,
                language=args.lang
            )
            print("\nSuggested commit:\n")
            print("----------------------------------------")
            print(commit_message)
            print("----------------------------------------")

        if is_editing_flow:
            edited_message = open_in_editor(commit_message)
            if not edited_message:
                print("Aborting commit due to empty message.")
                break
            commit(edited_message)
            break

        choice = get_user_choice()

        if choice == 'A':
            commit(commit_message)
            break
        elif choice == 'R':
            commit_message = None
            print("\n🔄 Regenerating...")
            continue
        elif choice == 'E':
            is_editing_flow = True
            continue
        elif choice == 'Q':
            print("Commit aborted by user.")
            break