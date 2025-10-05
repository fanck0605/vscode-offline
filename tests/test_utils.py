import tempfile
from pathlib import Path

import pytest

from vscode_offline.utils import (
    extract_filename_from_headers,
    get_vscode_version_from_server_installer,
)


def test_extract_filename_from_headers() -> None:
    headers = {
        "Content-Disposition": 'attachment; filename="example.txt"',
        "Content-Type": "text/plain",
    }
    assert extract_filename_from_headers(headers) == "example.txt"

    headers = {
        "Content-Disposition": 'inline; filename="report.pdf"',
        "Content-Type": "application/pdf",
    }
    assert extract_filename_from_headers(headers) == "report.pdf"

    headers = {
        "Content-Disposition": "attachment; filename*=UTF-8''%E2%82%AC%20rates.pdf",
        "Content-Type": "application/pdf",
    }
    assert extract_filename_from_headers(headers) == "€ rates.pdf"

    headers = {
        "Content-Type": "application/octet-stream",
    }
    assert extract_filename_from_headers(headers) is None

    headers: dict[str, str] = {}
    assert extract_filename_from_headers(headers) is None


def test_get_filename_from_vscode_download_response() -> None:
    headers = {
        "Content-Disposition": "attachment; filename=code_1.104.3-1759409451_amd64.deb; filename*=UTF-8''code_1.104.3-1759409451_amd64.deb",
        "Content-Type": "application/octet-stream",
    }
    assert extract_filename_from_headers(headers) == "code_1.104.3-1759409451_amd64.deb"


def test_get_filename_from_vsix_download_response() -> None:
    headers = {
        "Content-Disposition": "inline; filename=yzhang.markdown-all-in-one-3.6.3.vsix; filename*=utf-8''yzhang.markdown-all-in-one-3.6.3.vsix",
        "Content-Type": "application/vsix; api-version=7.2-preview.1",
    }
    assert (
        extract_filename_from_headers(headers)
        == "yzhang.markdown-all-in-one-3.6.3.vsix"
    )


def test_get_vscode_version_from_server_installer_success() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        version_dir = base / "commit-1234567890abcdef"
        version_dir.mkdir()
        (version_dir / "vscode-server-linux-x64.tar.gz").touch()
        result = get_vscode_version_from_server_installer(base, "linux-x64")
        assert result == "commit:1234567890abcdef"


def test_get_vscode_version_from_server_installer_multiple_found() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        v1 = base / "commit-1111111111111111"
        v2 = base / "commit-2222222222222222"
        v1.mkdir()
        v2.mkdir()
        (v1 / "vscode-server-linux-x64.tar.gz").touch()
        (v2 / "vscode-server-linux-x64.tar.gz").touch()
        with pytest.raises(ValueError, match="Multiple matching installers found"):
            get_vscode_version_from_server_installer(base, "linux-x64")


def test_get_vscode_version_from_server_installer_none_found() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        version_dir = base / "commit-1234567890abcdef"
        version_dir.mkdir()
        (version_dir / "vscode-server-linux-arm64.tar.gz").touch()
        with pytest.raises(ValueError, match="No matching installer found"):
            get_vscode_version_from_server_installer(base, "linux-x64")
