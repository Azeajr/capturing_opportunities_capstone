import time

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

log = structlog.get_logger()


class TimingAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Log the required information
        log.info(
            "processed_request",
            model_name=request.path_params.get("model_name"),
            request_path=request.url.path,
            duration=duration,
            session_id=response.headers.get("X-Session-Id"),
            initial_image_count=response.headers.get("X-Image-Count"),
            analytics=True,
        )

        return response
