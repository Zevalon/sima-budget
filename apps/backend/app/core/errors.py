from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class FieldError(BaseModel):
    field: str
    message: str


class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    code: str
    detail: str
    trace_id: str | None = None
    field_errors: list[FieldError] = Field(default_factory=list)


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _response(problem: ProblemDetail) -> JSONResponse:
    return JSONResponse(status_code=problem.status, content=problem.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        field_errors: list[FieldError] = []
        for item in exc.errors():
            location = ".".join(str(part) for part in item.get("loc", []))
            field_errors.append(FieldError(field=location, message=str(item.get("msg", "Invalid"))))
        return _response(
            ProblemDetail(
                type="https://sima.local/problems/validation-error",
                title="Data tidak valid",
                status=422,
                code="VALIDATION_ERROR",
                detail="Periksa kembali data yang dikirim.",
                trace_id=_trace_id(request),
                field_errors=field_errors,
            )
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        title = "Permintaan tidak dapat diproses"
        code = "HTTP_ERROR"
        if exc.status_code == 401:
            title, code = "Autentikasi diperlukan", "AUTHENTICATION_REQUIRED"
        elif exc.status_code == 403:
            title, code = "Akses ditolak", "PERMISSION_DENIED"
        elif exc.status_code == 404:
            title, code = "Data tidak ditemukan", "NOT_FOUND"
        elif exc.status_code == 409:
            title, code = "Konflik data", "CONFLICT"
        return _response(
            ProblemDetail(
                title=title,
                status=exc.status_code,
                code=code,
                detail=str(exc.detail),
                trace_id=_trace_id(request),
            )
        )
