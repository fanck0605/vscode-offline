from vscode_offline.utils import extract_filename_from_headers


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
