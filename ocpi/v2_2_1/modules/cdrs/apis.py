from fastapi import APIRouter, Depends, Response, Request

from ocpi.v2_2_1.modules.versions.enums import VersionNumber
from ocpi.v2_2_1.core.utils import get_auth_token, get_list
from ocpi.v2_2_1.core.status import OCPI_1000_GENERIC_SUCCESS_CODE
from ocpi.v2_2_1.core.schemas import OCPIResponse
from ocpi.v2_2_1.core.adapter import Adapter
from ocpi.v2_2_1.core.crud import Crud
from ocpi.v2_2_1.core.enums import ModuleID, RoleEnum
from ocpi.v2_2_1.core.dependencies import get_crud, get_adapter, pagination_filters

router = APIRouter(
    prefix='/cdrs',
)


@router.get("/", response_model=OCPIResponse)
async def get_cdrs(response: Response,
                   request: Request,
                   crud: Crud = Depends(get_crud),
                   adapter: Adapter = Depends(get_adapter),
                   filters: dict = Depends(pagination_filters)):
    auth_token = get_auth_token(request)

    data_list = await get_list(response, filters, ModuleID.cdrs, RoleEnum.cpo,
                               VersionNumber.v_2_2_1, crud, auth_token=auth_token)

    cdrs = []
    for data in data_list:
        cdrs.append(adapter.cdr_adapter(data).dict())
    return OCPIResponse(data=cdrs, **OCPI_1000_GENERIC_SUCCESS_CODE)
