from importlib.util import find_spec
from pathlib import Path
from typing import Optional
from typing import Union


# See https://github.com/psf/requests/issues/1081#issuecomment-428504128
class ForceMultipartDict(dict):
    def __bool__(self) -> bool:
        return True


def guess_mime_type_stdlib(url: Union[str, Path]) -> Optional[str]:  # pragma: no cover
    """
    Guesses the MIME type of a URL using the standard library.

    Args:
        url: The URL to guess the MIME type for.

    Returns:
        The guessed MIME type, or None if it could not be determined.
    """

    import mimetypes

    mime_type, _ = mimetypes.guess_type(str(url))  # Ensure URL is a string
    return mime_type


def guess_mime_type_magic(url: Union[str, Path]) -> Optional[str]:
    """
    Guesses the MIME type of a file using libmagic.

    Args:
        url: The path to the file or URL to guess the MIME type for.

    Returns:
        The guessed MIME type, or None if it could not be determined.
    """

    import magic  # type: ignore[import-not-found]

    try:
        return magic.from_file(str(url), mime=True)  # type: ignore[misc]
    except Exception:  # pragma: no cover
        # Handle libmagic exceptions gracefully
        return None


# Use the best option
guess_mime_type = guess_mime_type_magic if find_spec("magic") is not None else guess_mime_type_stdlib
