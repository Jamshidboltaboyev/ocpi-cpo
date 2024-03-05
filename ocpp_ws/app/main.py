from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from ocpp_ws.charge_point_v1_6 import ChargePoint
from ocpp_ws.api.routers import commands_router
from ocpp_ws.db.crud import (
    update_charge_point_on_disconnect,
    update_charge_point_on_connect
)
from ocpp_ws.app.dependencies import ACTIVE_CONNECTIONS

app = FastAPI()


class SocketAdapter:
    def __init__(self, websocket: WebSocket):
        self._ws = websocket

    async def recv(self) -> str:
        return await self._ws.receive_text()

    async def send(self, msg) -> None:
        await self._ws.send_text(msg)


class ConnectionManager:
    async def connect(self, websocket: WebSocket, charge_point_identify: str):
        await websocket.accept(subprotocol='ocpp1.6')
        ch_p = ChargePoint(charge_point_identify, SocketAdapter(websocket))
        ACTIVE_CONNECTIONS[charge_point_identify] = ch_p
        await update_charge_point_on_connect(charge_point_identify)
        await ch_p.start()

    async def disconnect(self, charge_point_identify: str):
        await update_charge_point_on_disconnect(charge_point_identify)


manager = ConnectionManager()


@app.websocket("/ws/{charge_point_identify}")
async def websocket_endpoint(websocket: WebSocket, charge_point_identify: str):
    try:
        await manager.connect(websocket, charge_point_identify)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(charge_point_identify)


app.include_router(commands_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=app,
        host='localhost',
        port=9000
    )