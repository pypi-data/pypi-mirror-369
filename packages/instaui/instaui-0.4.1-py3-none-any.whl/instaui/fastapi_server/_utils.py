from typing import Any, Dict, List, Optional, Sequence
from fastapi import Response
from instaui.runtime._app import get_app_slot
from instaui.response import response_data
import pydantic


class ResponseData(pydantic.BaseModel):
    values: Optional[List[Any]] = None
    types: Optional[Sequence[int]] = None


def update_app_page_info(data: Dict):
    app = get_app_slot()

    page_info = data.get("page", {})
    app._page_path = page_info["path"]

    if "params" in page_info:
        app._page_params = page_info["params"]

    if "queryParams" in page_info:
        app._query_params = page_info["queryParams"]


def response_web_data(
    outputs_binding_count: int, result: Any, response: Optional[Response] = None
):
    new_result = result
    if response is not None:
        response_interceptor, new_result = _extract_response_interceptor(
            outputs_binding_count, result
        )
        if response_interceptor is not None:
            response_interceptor(response)

    return ResponseData(**response_data(outputs_binding_count, new_result))


def _extract_response_interceptor(outputs_binding_count: int, result: Any):
    if outputs_binding_count == 0:
        if callable(result):
            return result, None
        return None, result

    if outputs_binding_count == 1:
        if isinstance(result, tuple) and len(result) == 2 and callable(result[1]):
            return result[1], result[:-1]
        return None, result

    if (
        isinstance(result, tuple)
        and len(result) - outputs_binding_count == 1
        and callable(result[-1])
    ):
        return result[-1], result[:-1]
    return None, result
