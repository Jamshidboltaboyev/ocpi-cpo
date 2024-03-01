from typing import Any, List

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from ocpi.v2_2_1.core.endpoints import ENDPOINTS
from ocpi.v2_2_1.middlewares import ExceptionHandlerMiddleware

from ocpi.v2_2_1.modules.versions.api import router as versions_router, versions_v_2_2_1_router
from ocpi.v2_2_1.modules.versions.enums import VersionNumber
from ocpi.v2_2_1.modules.versions.schemas import Version
from ocpi.v2_2_1.core.dependencies import get_crud, get_adapter, get_versions, get_endpoints
from ocpi.v2_2_1.core.enums import RoleEnum
from ocpi.v2_2_1.core.config import settings
from ocpi.v2_2_1.core.data_types import URL

from ocpi.v2_2_1.core.push import http_router as http_push_router, websocket_router as websocket_push_router
from ocpi.v2_2_1.routers import v_2_2_1_cpo_router, v_2_2_1_emsp_router


def get_application(
        version_numbers: List[VersionNumber],
        roles: List[RoleEnum],
        crud: Any,
        adapter: Any,
        http_push: bool = False,
        websocket_push: bool = False,
) -> FastAPI:
    _app = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url=f'/{settings.OCPI_PREFIX}/docs',
        openapi_url=f"/{settings.OCPI_PREFIX}/openapi.json"
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.add_middleware(ExceptionHandlerMiddleware)

    _app.include_router(
        versions_router,
        prefix=f'/{settings.OCPI_PREFIX}',
    )

    if http_push:
        _app.include_router(
            http_push_router,
            prefix=f'/{settings.PUSH_PREFIX}',
        )

    if websocket_push:
        _app.include_router(
            websocket_push_router,
            prefix=f'/{settings.PUSH_PREFIX}',
        )

    versions = []
    version_endpoints = {}

    if VersionNumber.v_2_2_1 in version_numbers:
        _app.include_router(
            versions_v_2_2_1_router,
            prefix=f'/{settings.OCPI_PREFIX}',
        )

        versions.append(
            Version(
                version=VersionNumber.v_2_2_1,
                url=URL(f'https://{settings.OCPI_HOST}/{settings.OCPI_PREFIX}/{VersionNumber.v_2_2_1.value}/details')
            ).dict(),
        )

        version_endpoints[VersionNumber.v_2_2_1] = []

        if RoleEnum.cpo in roles:
            _app.include_router(
                v_2_2_1_cpo_router,
                prefix=f'/{settings.OCPI_PREFIX}/cpo/{VersionNumber.v_2_2_1.value}',
                tags=['CPO']
            )
            version_endpoints[VersionNumber.v_2_2_1] += ENDPOINTS[VersionNumber.v_2_2_1][RoleEnum.cpo]

        if RoleEnum.emsp in roles:
            _app.include_router(
                v_2_2_1_emsp_router,
                prefix=f'/{settings.OCPI_PREFIX}/emsp/{VersionNumber.v_2_2_1.value}',
                tags=['EMSP']
            )
            version_endpoints[VersionNumber.v_2_2_1] += ENDPOINTS[VersionNumber.v_2_2_1][RoleEnum.emsp]

    def override_get_crud():
        return crud

    _app.dependency_overrides[get_crud] = override_get_crud

    def override_get_adapter():
        return adapter

    _app.dependency_overrides[get_adapter] = override_get_adapter

    def override_get_versions():
        return versions

    _app.dependency_overrides[get_versions] = override_get_versions

    def override_get_endpoints():
        return version_endpoints

    _app.dependency_overrides[get_endpoints] = override_get_endpoints

    return _app
