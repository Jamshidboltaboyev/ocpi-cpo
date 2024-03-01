from ocpi.core import status
from ocpi.core.exceptions import AuthorizationOCPIError, NotFoundOCPIError
from ocpi.core.schemas import OCPIResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse
from pydantic import ValidationError


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ):
        try:
            response = await call_next(request)
        except AuthorizationOCPIError as e:
            raise HTTPException(403, str(e)) from e
        except NotFoundOCPIError as e:
            raise HTTPException(404, str(e)) from e
        except ValidationError:
            response = JSONResponse(
                OCPIResponse(
                    data=[],
                    **status.OCPI_3000_GENERIC_SERVER_ERROR,
                ).dict()
            )
        return response
