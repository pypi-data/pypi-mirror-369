from pathlib import Path

from office_to_pdf_client import OfficeToPdfClient


def client_example(office_to_pdf_url: str, input_file_path: str | Path):
    headers = {}
    if isinstance(input_file_path, str):
        input_file_path = Path(input_file_path)
    output_file_path = input_file_path.with_suffix(".pdf")
    client = OfficeToPdfClient(office_to_pdf_url)
    if headers:
        client.add_headers(headers)
    client.convert_to_pdf(input_file_path, output_file_path, single_page_sheets=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--office_to_pdf_url", type=str, default="http://127.0.0.1:8000")
    parser.add_argument("--input", type=str, default="./examples/test.xlsx")
    args = parser.parse_args()
    client_example(args.office_to_pdf_url, args.input)
