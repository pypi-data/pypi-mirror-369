from typing import TypeVar

from .raw_api.types import Response

T = TypeVar("T")

class NotFound(Exception):
    pass

def get_body_and_handle_err(response: Response[T]) -> T:
    if response.status_code == 404:
        raise NotFound(response)

    if response.status_code != 200:
        raise Exception(response)

    if response.parsed is None:
        raise Exception("Error parsing response")

    return response.parsed
