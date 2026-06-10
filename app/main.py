"""FastAPI application entry point."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse

from app.config import EnvSettingsProvider, Settings, SettingsProvider
from app.email_utils import EmailValidationError, validate_email
from app.security import SecurityMiddleware, hash_domain, parse_outlook_email_address
from app.templates import outlook_autodiscover, outlook_get_neutral_response, thunderbird_autoconfig

XML_CONTENT_TYPE = "application/xml; charset=utf-8"

_settings_provider: SettingsProvider = EnvSettingsProvider()


def get_settings_provider() -> SettingsProvider:
    return _settings_provider


def get_settings(
    provider: Annotated[SettingsProvider, Depends(get_settings_provider)],
) -> Settings:
    return provider.get_settings()


def _domain_error_response(settings: Settings) -> JSONResponse:
    if settings.return_404_for_unknown_domain:
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return JSONResponse(status_code=400, content={"detail": "Configuration not available"})


def _invalid_request() -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": "Invalid request"})


def _xml_response(content: str) -> Response:
    return Response(content=content, media_type=XML_CONTENT_TYPE)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = _settings_provider.get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
    yield


def create_app(settings_provider: SettingsProvider | None = None) -> FastAPI:
    global _settings_provider
    if settings_provider is not None:
        _settings_provider = settings_provider

    settings = _settings_provider.get_settings()

    app = FastAPI(
        title=settings.app_name,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.add_middleware(SecurityMiddleware, settings=settings)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    async def root(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
        return {"name": settings.app_name, "status": "running"}

    async def _thunderbird_config(
        request: Request,
        emailaddress: str | None,
        settings: Settings,
    ) -> Response:
        if not settings.thunderbird_enabled:
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        validated, error = validate_email(emailaddress, settings)
        if error == EmailValidationError.EMPTY:
            return _invalid_request()
        if error is not None:
            request.state.domain_allowed = False
            return _domain_error_response(settings)

        request.state.domain_allowed = True
        request.state.domain_hash = hash_domain(validated.domain)  # type: ignore[union-attr]
        xml = thunderbird_autoconfig(validated, settings)  # type: ignore[arg-type]
        return _xml_response(xml)

    @app.get("/mail/config-v1.1.xml")
    async def thunderbird_config(
        request: Request,
        settings: Annotated[Settings, Depends(get_settings)],
        emailaddress: Annotated[str | None, Query()] = None,
    ) -> Response:
        return await _thunderbird_config(request, emailaddress, settings)

    @app.get("/.well-known/autoconfig/mail/config-v1.1.xml")
    async def thunderbird_config_wellknown(
        request: Request,
        settings: Annotated[Settings, Depends(get_settings)],
        emailaddress: Annotated[str | None, Query()] = None,
    ) -> Response:
        return await _thunderbird_config(request, emailaddress, settings)

    @app.post("/autodiscover/autodiscover.xml")
    async def outlook_autodiscover_post(
        request: Request,
        settings: Annotated[Settings, Depends(get_settings)],
    ) -> Response:
        if not settings.outlook_enabled:
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        body = await request.body()
        if len(body) > settings.max_request_body_bytes:
            return JSONResponse(status_code=413, content={"detail": "Request entity too large"})

        email_raw = parse_outlook_email_address(body)
        if not email_raw:
            return _invalid_request()

        validated, error = validate_email(email_raw, settings)
        if error is not None:
            request.state.domain_allowed = False
            if error == EmailValidationError.DOMAIN_NOT_ALLOWED:
                return _domain_error_response(settings)
            return _invalid_request()

        request.state.domain_allowed = True
        request.state.domain_hash = hash_domain(validated.domain)  # type: ignore[union-attr]
        xml = outlook_autodiscover(validated, settings)  # type: ignore[arg-type]
        return _xml_response(xml)

    @app.get("/autodiscover/autodiscover.xml")
    async def outlook_autodiscover_get() -> Response:
        return _xml_response(outlook_get_neutral_response())

    return app


app = create_app()
