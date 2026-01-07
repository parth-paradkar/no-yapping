# no-yapping
Too many comments dilute the importance of any single comment. Code should be self-explanatory through good variable naming, less complexity, etc.  

no-yapping is a Flake8 plugin that detects functions with excessive comments.

Built with Claude for fun :)

## Installation

```bash
pip install no-yapping
```

## Usage

```bash
flake8 --select=NYP myfile.py
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--max-comment-ratio` | 0.3 | Maximum allowed comment-to-code ratio |
| `--min-function-lines` | 10 | Minimum function size to check |

## Error Codes

- `NYP001`: Function has too many comments
