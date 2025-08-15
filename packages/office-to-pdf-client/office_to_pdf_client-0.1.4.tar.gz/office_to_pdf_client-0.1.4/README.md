# office-to-pdf-client

This is a client for [office-to-pdf-serve](https://github.com/first-automation/office-to-pdf-serve).

## Usage

### 1. Installation

```
pip install office-to-pdf-client
```

### 2. Prerequisites
Start the server of [office-to-pdf-serve](https://github.com/first-automation/office-to-pdf-serve) using docker compose.
(In the case of docker compose, the server will start at "http://127.0.0.1:8000")

### 3. Client Usage Example

```python
from pathlib import Path

from office_to_pdf_client import OfficeToPdfClient

office_to_pdf_url = "http://127.0.0.1:8000"
office_file_path = Path("./examples/test.xlsx")
output_file_path = Path("./examples/test.pdf")
client = OfficeToPdfClient(office_to_pdf_url)
client.convert_to_pdf(office_file_path, output_file_path)
```

※The endpoint ("/convert_to_pdf") is internally combined with the URL and sent to the backend as "http://127.0.0.1:8000/convert_to_pdf".
