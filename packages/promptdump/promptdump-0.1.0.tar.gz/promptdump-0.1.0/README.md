# Promptdump

A command-line tool to quickly gather and format code and directory structures for AI prompts.
This can be useful for creating prompts for e.g. Google AI Studio, which has a large context limit.

- 📁 Formats the relevant files in an entire codebase into a prompt.
- 📋 Copies output to clipboard by default for quick pasting into AI tools.

## Installation

```bash
# Install using pipx (recommended)
pipx install promptdump

# Or run without installing
uvx promptdump
```

## Usage

### Examples

Scan current directory (default extensions: .md, .py, .cpp, .hpp, .js, .ts, .java, .go, .rs, .c, .h) and copy to clipboard:
```bash
promptdump
```

Scan specific file types:
```bash
# Only Python and JavaScript files
promptdump .py .js
```

Include specific files by name:
```bash
# Include specific files regardless of extension
promptdump -f pyproject.toml README.md
```

Combine file types and specific files:
```bash
# Include Python files and specific config files
promptdump .py -f requirements.txt config.json
```

Scan a different directory:
```bash
promptdump -d /path/to/project
```

Save output to a file:
```bash
promptdump -o output.txt
```

Save output to stdout (useful for piping to other commands):
```bash
promptdump -o -
```

Use a custom exclude file (default: .gitignore):
```bash
promptdump -e .gitignore_custom
```

Enable verbose output:
```bash
promptdump -v
```

## Options

- `[EXTENSIONS]` - File extensions to include (e.g., .py .js .ts)
- `-f, --files [FILES ...]` - Include specific files by name (e.g., README.md)
AI- `-d, --directory PATH` - Directory to scan (default: current directory)
- `-o, --output FILE` - Write output to file instead of clipboard
- `-e, --exclude FILE` - File containing patterns to exclude (default: .gitignore)
- `-v, --verbose` - Enable verbose output
- `--help` - Show help message and exit

