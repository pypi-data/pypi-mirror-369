import weakref
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx

from ..handlers import ErrorHandler, ResponseBuilder
from ..models import HivetraceResponse
from .base import BaseHivetraceSDK


class SyncHivetraceSDK(BaseHivetraceSDK):
    """
    Sync implementation of HiveTrace SDK.

    Uses httpx.Client for blocking HTTP operations.

    Usage:
        with SyncHivetraceSDK() as client:
            result = client.input(app_id, message)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.session = httpx.Client()
        self.async_mode = False

        self._finalizer = weakref.finalize(
            self, self._cleanup_sync_session, self.session
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def _cleanup_sync_session(session):
        """Safely closes sync session through finalizer."""
        try:
            if hasattr(session, "_transport") and not session.is_closed:
                session.close()
        except Exception:
            pass

    def _send_request(
        self, endpoint: str, payload: Dict[str, Any]
    ) -> HivetraceResponse:
        request_args = self._build_request_args(endpoint, payload)
        try:
            response = self.session.post(**request_args)
            response.raise_for_status()

            api_data = response.json()
            return ResponseBuilder.build_response_from_api(api_data)

        except httpx.HTTPStatusError as e:
            return ErrorHandler.handle_http_error(e)
        except httpx.ConnectError as e:
            return ErrorHandler.handle_connection_error(e)
        except httpx.TimeoutException as e:
            return ErrorHandler.handle_timeout_error(e)
        except httpx.RequestError as e:
            return ErrorHandler.handle_request_error(e)
        except ValueError as e:
            return ErrorHandler.handle_json_decode_error(e)
        except Exception as e:
            return ErrorHandler.handle_unexpected_error(e)

    def _send_files(
        self, endpoint: str, files: List[Tuple[str, bytes, str]]
    ) -> HivetraceResponse:
        request_args = self._build_files_request_args(endpoint, files)
        try:
            response = self.session.post(**request_args)
            response.raise_for_status()

            api_data = response.json()
            return ResponseBuilder.build_response_from_api(api_data)

        except httpx.HTTPStatusError as e:
            return ErrorHandler.handle_http_error(e)
        except httpx.ConnectError as e:
            return ErrorHandler.handle_connection_error(e)
        except httpx.TimeoutException as e:
            return ErrorHandler.handle_timeout_error(e)
        except httpx.RequestError as e:
            return ErrorHandler.handle_request_error(e)
        except ValueError as e:
            return ErrorHandler.handle_json_decode_error(e)
        except Exception as e:
            return ErrorHandler.handle_unexpected_error(e)

    def _get_blocking_status(self, endpoint: str) -> Optional[bool]:
        url = f"{self.hivetrace_url}/{endpoint.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self.hivetrace_access_token}"}
        try:
            response = self.session.get(
                url, headers=headers, timeout=self._DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            return data.get("blocked")
        except Exception:
            return None

    def input(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
        files: Optional[List[Tuple[str, bytes, str]]] = None,
    ) -> HivetraceResponse:
        payload = self._build_message_payload(
            application_id, message, additional_parameters
        )
        process_response = self._send_request("/process_request/", payload)
        if files:
            analysis_id = self._extract_analysis_id(process_response)
            if analysis_id:
                self._send_files(
                    f"/user_prompt_analysis/{analysis_id}/attach_files", files
                )
        analysis_id = self._extract_analysis_id(process_response)
        if analysis_id:
            blocked = self._get_blocking_status(
                f"/user_prompt_analysis/{analysis_id}/check_blocking"
            )
            self._set_blocked(process_response, blocked)
        return process_response

    def output(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
        files: Optional[List[Tuple[str, bytes, str]]] = None,
    ) -> HivetraceResponse:
        payload = self._build_message_payload(
            application_id, message, additional_parameters
        )
        process_response = self._send_request("/process_response/", payload)
        if files:
            analysis_id = self._extract_analysis_id(process_response)
            if analysis_id:
                self._send_files(
                    f"/llm_response_analysis/{analysis_id}/attach_files", files
                )
        analysis_id = self._extract_analysis_id(process_response)
        if analysis_id:
            blocked = self._get_blocking_status(
                f"/llm_response_analysis/{analysis_id}/check_blocking"
            )
            self._set_blocked(process_response, blocked)
        return process_response

    def function_call(
        self,
        application_id: str,
        tool_call_id: str,
        func_name: str,
        func_args: str,
        func_result: Optional[Union[Dict, str]] = None,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        payload = self._build_function_call_payload(
            application_id,
            tool_call_id,
            func_name,
            func_args,
            func_result,
            additional_parameters,
        )
        return self._send_request("/process_tool_call/", payload)

    def close(self) -> None:
        """Syncly closes HTTP session."""
        if self._closed:
            return
        self._closed = True
        self.session.close()
