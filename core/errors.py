from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        errors = []

        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
            })

        return JSONResponse(
            status_code=422,
            content={
                "message": "Request validation failed",
                "errors": errors,
            },
        )