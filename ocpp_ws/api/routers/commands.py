from fastapi import APIRouter, Request
from ocpp_ws.api.schemas.commands import StartSession, StopSession, CommandResult
from ocpp_ws.api.services.commands import start_session, stop_session
from ocpp_ws.api.schemas.core import OCPIResponse, OCPI_1000_GENERIC_SUCESS_CODE

router = APIRouter(prefix="/ocpi/cpo/2.2.1/commands")


@router.post("/START_SESSION", response_model=OCPIResponse)
async def command_start_router(request: Request, data: StartSession):

    result: CommandResult = await start_session(start_session_data=data)
    return OCPIResponse(
        data=result,
        **OCPI_1000_GENERIC_SUCESS_CODE
    )


@router.post("/STOP_SESSION", response_model=OCPIResponse)
async def command_stop_router(request: Request, data: StopSession):
    result = await stop_session(session_id=data.session_id)
    return OCPIResponse(
        data=result,
        **OCPI_1000_GENERIC_SUCESS_CODE
    )
