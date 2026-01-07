import ast
import tokenize
from io import StringIO
from typing import Generator

__version__ = "0.1.0"


class NoYappingChecker:
    """Flake8 plugin that detects functions with excessive comments."""

    name = "no-yapping"
    version = __version__

    # Default configuration
    max_comment_ratio = 0.3
    min_function_lines = 10

    def __init__(self, tree: ast.AST, filename: str) -> None:
        self.tree = tree
        self.filename = filename

    @classmethod
    def add_options(cls, parser) -> None:
        """Register configuration options with flake8."""
        parser.add_option(
            "--max-comment-ratio",
            type=float,
            default=0.3,
            parse_from_config=True,
            help="Maximum allowed comment-to-code ratio (default: 0.3)",
        )
        parser.add_option(
            "--min-function-lines",
            type=int,
            default=10,
            parse_from_config=True,
            help="Minimum function size to check (default: 10)",
        )

    @classmethod
    def parse_options(cls, options) -> None:
        """Parse configuration options from flake8."""
        cls.max_comment_ratio = options.max_comment_ratio
        cls.min_function_lines = options.min_function_lines

    def run(self) -> Generator[tuple[int, int, str, type], None, None]:
        """Run the checker and yield violations."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                source = f.read()
        except (OSError, IOError):
            return

        comment_lines = self._get_comment_lines(source)
        functions = self._get_functions(self.tree)

        for func in functions:
            start_line = func.lineno
            end_line = func.end_lineno or start_line
            total_lines = end_line - start_line + 1

            if total_lines < self.min_function_lines:
                continue

            comments_in_func = sum(
                1 for line in comment_lines if start_line <= line <= end_line
            )

            ratio = comments_in_func / total_lines

            if ratio > self.max_comment_ratio:
                yield (
                    func.lineno,
                    func.col_offset,
                    f"NYP001 Function '{func.name}' has too many comments "
                    f"({ratio:.0%} > {self.max_comment_ratio:.0%})",
                    type(self),
                )

    def _get_comment_lines(self, source: str) -> set[int]:
        """Extract line numbers that contain comments."""
        comment_lines = set()
        try:
            tokens = tokenize.generate_tokens(StringIO(source).readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    comment_lines.add(token.start[0])
        except tokenize.TokenizeError:
            pass
        return comment_lines

    def _get_functions(self, tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
        """Extract all function definitions from the AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node)
        return functions
