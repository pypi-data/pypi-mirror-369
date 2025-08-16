from promptdump.promptdump import make_prompt
import argparse
import sys
import os
import pyperclip


def main():
    parser = argparse.ArgumentParser(description="Scan a directory and process files.")
    parser.add_argument(
        "extensions",
        nargs="*",
        default=[".md", ".py", ".cpp", ".hpp", ".js", ".ts", ".java", ".go", ".rs", ".c", ".h"],
        help="File extensions to include (e.g., .py .js .ts)",
    )
    parser.add_argument("-f", "--files", nargs="*", default=["pyproject.toml"], help="Files to include")
    parser.add_argument(
        "-d",
        "--directory",
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file (use - for stdout, default: clipboard)",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        default=".gitignore",
        help="File containing patterns to exclude (default: .gitignore)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    args = parser.parse_args()
    result = make_prompt(args)
    # Output the result
    if args.output == "-":
        # Write to stdout
        try:
            sys.stdout.write(result)
            if not result.endswith("\n"):
                sys.stdout.write("\n")
            sys.stdout.flush()
        except BrokenPipeError:
            # Handle broken pipe (e.g., when piped to head)
            sys.stderr.close()
            sys.exit(0)
        except Exception as e:
            print(f"Error writing to stdout: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.output:
        # Write to file
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(
                f"Output written to: {os.path.abspath(args.output)}, {len(result):,d} characters long.", file=sys.stderr
            )
        except Exception as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Default to clipboard
        pyperclip.copy(result)
        print(f"Output copied to clipboard, {len(result):,d} characters long.", file=sys.stderr)


if __name__ == "__main__":
    main()
