import pytest

from vscode_offline.install import (
    _extract_commit_from_code_version_output,  # pyright: ignore[reportPrivateUsage]
)


def test_extract_commit_from_valid_output() -> None:
    # Simulate output like: b'code 1.80.0 (commit 1234567890abcdef1234567890abcdef12345678)\n'
    commit = "1234567890abcdef1234567890abcdef12345678"
    output = f"code 1.80.0 (commit {commit})\n".encode("utf-8")
    assert _extract_commit_from_code_version_output(output) == commit


def test_extract_commit_from_invalid_output() -> None:
    output = b"code 1.80.0 (no commit info here)\n"
    with pytest.raises(
        ValueError, match="Cannot determine commit hash from code version"
    ):
        _extract_commit_from_code_version_output(output)


def test_extract_commit_from_output_short_commit() -> None:
    # Should not match if commit is too short (<40 chars)
    output = b"code 1.80.0 (commit 1234567890abcdef)\n"
    with pytest.raises(ValueError):
        _extract_commit_from_code_version_output(output)
