import os
import sys
current_dir = os.getcwd()
sys.path.append(current_dir + "/src")

from pathlib import Path
from office_to_pdf_client._utils import guess_mime_type


def test_guess_mime_type():
    # 入力のパスを設定
    input_file_path = Path('input.xlsx')
    mime_type = guess_mime_type(input_file_path)
    assert mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
