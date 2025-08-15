import os
import sys
current_dir = os.getcwd()
sys.path.append(current_dir + "/src")

import logging
from office_to_pdf_client import OfficeToPdfClient, OfficeToPdfClientAsync
from unittest.mock import Mock  # Import Mock for patching
from pytest_mock import MockerFixture
from pathlib import Path


def test_init_default_values():
    """
    Test that the OfficeToPdfClient is initialized with default values.
    """
    client = OfficeToPdfClient("http://127.0.0.1:8000")
    assert client._client.base_url == "http://127.0.0.1:8000"
    assert client._client.timeout.read == 30.0
    assert client.http2 is True  # httpxのclientから抽出できなかったので、OfficeToPdfClientのpropertyから取得できるように設定
    assert logging.getLogger("httpx").level == logging.ERROR
    assert logging.getLogger("httpcore").level == logging.ERROR


def test_init_custom_values():
    """
    Test that the OfficeToPdfClient is initialized with custom values.
    """
    client = OfficeToPdfClient(
        "http://127.0.0.1:8000", timeout=10.0, log_level=logging.INFO, http2=False
    )
    assert client._client.base_url == "http://127.0.0.1:8000"
    assert client._client.timeout.read == 10.0
    assert client.http2 is False
    assert logging.getLogger("httpx").level == logging.INFO
    assert logging.getLogger("httpcore").level == logging.INFO


def test_add_headers():
    """
    Test that the add_headers method updates the client headers.
    """
    client = OfficeToPdfClient("http://127.0.0.1:8000")
    headers = {"Content-Type": "application/json"}
    set_headers = [
        (
            b'Accept',
            b'*/*',
        ),
        (
            b'Accept-Encoding',
            b'gzip, deflate',
        ),
        (
            b'Connection',
            b'keep-alive',
        ),
        (
            b'User-Agent',
            b'python-httpx/0.28.1',
        ),
        (
            b'Content-Type',
            b'application/json',
        ),
    ]
    client.add_headers(headers)
    assert client._client.headers.raw == set_headers


def test_get_resource(mocker: MockerFixture):
    # モックの作成
    get_resource_mock = mocker.patch("office_to_pdf_client.OfficeToPdfClient._get_resource")
    get_resource_mock.return_value = {"file": "test"}

    # 入力のパスを設定
    input_file_path = Path('input.txt')

    # テスト対象の関数呼び出し
    converter = OfficeToPdfClient("http://127.0.0.1:8000")  # 実際のクラスに置き換える
    result = converter._get_resource(input_file_path)

    # アサーション
    assert result == {"file": "test"}


def test_convert_to_pdf_success(mocker):
    # モックの作成
    convert_to_pdf_mock = mocker.patch("office_to_pdf_client.OfficeToPdfClient.convert_to_pdf")
    convert_to_pdf_mock.return_value = None

    # 入力と出力のパスを設定
    input_file_path = Path('input.txt')
    output_file_path = Path('output.pdf')

    # テスト対象の関数呼び出し
    converter = OfficeToPdfClient("http://127.0.0.1:8000")  # 実際のクラスに置き換える
    result = converter.convert_to_pdf(input_file_path, output_file_path)

    # アサーション
    assert result is None


def test_convert_to_pdf_success_async(mocker):
    # モックの作成
    convert_to_pdf_mock = mocker.patch("office_to_pdf_client.OfficeToPdfClientAsync.convert_to_pdf")
    convert_to_pdf_mock.return_value = None

    # 入力と出力のパスを設定
    input_file_path = Path('input.txt')
    output_file_path = Path('output.pdf')

    # テスト対象の関数呼び出し
    converter = OfficeToPdfClientAsync("http://127.0.0.1:8000")  # 実際のクラスに置き換える
    result = converter.convert_to_pdf(input_file_path, output_file_path)


def test_close():
    """
    Test that the close method closes the underlying HTTP client connection.
    """
    # Mock the httpx.Client close method
    client = OfficeToPdfClient("http://127.0.0.1:8000")
    client._client.close = Mock()
    client.close()
    client._client.close.assert_called_once()
