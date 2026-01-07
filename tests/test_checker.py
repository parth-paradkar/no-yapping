import ast
import tempfile
import os
from no_yapping.checker import NoYappingChecker


def run_checker(source: str, max_ratio: float = 0.3, min_lines: int = 10) -> list:
    """Helper to run the checker on source code."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source)
        f.flush()
        filename = f.name

    try:
        tree = ast.parse(source)
        NoYappingChecker.max_comment_ratio = max_ratio
        NoYappingChecker.min_function_lines = min_lines
        checker = NoYappingChecker(tree, filename)
        return list(checker.run())
    finally:
        os.unlink(filename)


def test_function_with_acceptable_comments():
    """Function with few comments should pass."""
    source = """
def my_function():
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    # one comment
    return x + y
"""
    errors = run_checker(source, max_ratio=0.3, min_lines=5)
    assert len(errors) == 0


def test_function_with_excessive_comments():
    """Function with too many comments should fail."""
    source = """
def my_function():
    # comment 1
    # comment 2
    # comment 3
    # comment 4
    # comment 5
    x = 1
    y = 2
    return x + y
"""
    errors = run_checker(source, max_ratio=0.3, min_lines=5)
    assert len(errors) == 1
    assert "NYP001" in errors[0][2]
    assert "my_function" in errors[0][2]


def test_small_function_is_skipped():
    """Functions below minimum size should not be checked."""
    source = """
def tiny():
    # comment
    # comment
    # comment
    return 1
"""
    errors = run_checker(source, max_ratio=0.3, min_lines=10)
    assert len(errors) == 0


def test_docstrings_not_counted():
    """Docstrings should not count as comments."""
    source = """
def documented():
    '''
    This is a long docstring.
    It has multiple lines.
    But it should not count as comments.
    '''
    x = 1
    y = 2
    z = 3
    return x + y + z
"""
    errors = run_checker(source, max_ratio=0.3, min_lines=5)
    assert len(errors) == 0


def test_async_function():
    """Async functions should also be checked."""
    source = """
async def my_async():
    # comment 1
    # comment 2
    # comment 3
    # comment 4
    # comment 5
    x = 1
    y = 2
    return x + y
"""
    errors = run_checker(source, max_ratio=0.3, min_lines=5)
    assert len(errors) == 1
    assert "my_async" in errors[0][2]


def test_custom_threshold():
    """Custom threshold should be respected."""
    source = """
def my_function():
    # comment 1
    # comment 2
    # comment 3
    # comment 4
    x = 1
    y = 2
    z = 3
    a = 4
    return x
"""
    # With 50% threshold, 4 comments in 11 lines (~36%) should pass
    errors = run_checker(source, max_ratio=0.5, min_lines=5)
    assert len(errors) == 0

    # With 30% threshold, same code should fail
    errors = run_checker(source, max_ratio=0.3, min_lines=5)
    assert len(errors) == 1
