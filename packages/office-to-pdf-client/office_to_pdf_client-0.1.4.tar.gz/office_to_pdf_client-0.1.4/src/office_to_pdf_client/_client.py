import logging
from contextlib import ExitStack
from pathlib import Path
from types import TracebackType
from typing import Optional

from httpx import AsyncClient, Client
from httpx._types import RequestFiles

from office_to_pdf_client._utils import guess_mime_type


logger = logging.getLogger(__name__)


class OfficeToPdfClient:
    def __init__(
        self,
        host: str,
        *,
        timeout: float = 30.0,
        log_level: int = logging.ERROR,
        http2: bool = True,
        api_route: str = "/convert_to_pdf"
    ):
        """_summary_
        Initialize a new office-to-pdf instance.

        Args:
            host (str): _description_
            timeout (float, optional): _description_. Defaults to 30.0.
            log_level (int, optional): _description_. Defaults to logging.ERROR.
            http2 (bool, optional): _description_. Defaults to True.
            api_route (str, optional): _description_. Defaults to /convert_to_pdf.
        """
        # Configure the client
        self._http2 = http2
        self._route = api_route
        self._stack = ExitStack()
        self._client = Client(base_url=host, timeout=timeout, http2=http2)

        # Set the log level
        logging.getLogger("httpx").setLevel(log_level)
        logging.getLogger("httpcore").setLevel(log_level)

    @property
    def http2(self):
        return self._http2

    def add_headers(self, header: dict[str, str]) -> None:
        """
        Update the httpx Client headers with the given values.

        Args:
            header (Dict[str, str]): A dictionary of header names and values to add.
        """
        self._client.headers.update(header)

    def _get_resource(self, filepath: Path) -> RequestFiles:
        """
        Deals with opening all provided files for multi-part uploads, including
        pushing their new contexts onto the stack to ensure resources like file
        handles are cleaned up
        """
        resource = {}
        filename = filepath.name
        # Helpful but not necessary to provide the mime type when possible
        mime_type = guess_mime_type(filepath)
        if mime_type is not None:
            resource.update(
                {"file": (filename, self._stack.enter_context(filepath.open("rb")), mime_type)},
            )
        else:  # pragma: no cover
            resource.update({"file": (filename, self._stack.enter_context(filepath.open("rb")))})  # type: ignore [dict-item]
        return resource

    def convert_to_pdf(
        self,
        input_file_path: Path,
        output_file_path: Path,
        sheet_names: list[str] | None = None,
        single_page_sheets: bool = False,
    ) -> None:
        """
        convert a single file to PDF.

        Args:
            input_file_path (Path): The path to the file to be converted.
            output_file_path (Path): The path to the file for output.
            sheet_names (list[str] | None): The names of the sheets to be converted (optional).
            single_page_sheets (bool): Whether to convert the sheets to single page sheets (optional).

        Returns:
            None
        """

        response = self._client.post(
            url=self._route,
            files=self._get_resource(input_file_path),
            data={"sheet_names": sheet_names} if sheet_names is not None else None,
            params={"single_page_sheets": single_page_sheets},
        )
        response.raise_for_status()
        output_file_path.write_bytes(response.content)

    def close(self) -> None:
        """
        Close the underlying HTTP client connection.
        """
        self._client.close()

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Exit the runtime context related to this object.

        This method ensures that the client connection is closed when exiting a context manager.

        Args:
            exc_type: The type of the exception that caused the context to be exited, if any.
            exc_val: The instance of the exception that caused the context to be exited, if any.
            exc_tb: A traceback object encoding the stack trace, if an exception occurred.
        """
        self.close()


class OfficeToPdfClientAsync(OfficeToPdfClient):
    def __init__(
        self,
        host: str,
        *,
        timeout: float = 30.0,
        log_level: int = logging.ERROR,
        http2: bool = True,
        api_route: str = "/convert_to_pdf"
    ):
        super().__init__(host, timeout=timeout, log_level=log_level, http2=http2, api_route=api_route)
        self._client = AsyncClient(base_url=host, timeout=timeout, http2=http2)

    async def convert_to_pdf(
        self,
        input_file_path: Path,
        output_file_path: Path,
        sheet_names: list[str] | None = None,
        single_page_sheets: bool = False,
    ) -> None:
        response = await self._client.post(
            url=self._route,
            files=self._get_resource(input_file_path),
            data={"sheet_names": sheet_names} if sheet_names is not None else None,
            params={"single_page_sheets": single_page_sheets},
        )
        response.raise_for_status()
        output_file_path.write_bytes(response.content)

    async def close(self) -> None:
        await self._client.aclose()
