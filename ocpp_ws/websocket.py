from starlette.websockets import WebSocket, WebSocketDisconnect

from ocpp_ws.charge_point_v1_6 import ChargePoint

active_connection = {}

from fastapi import APIRouter

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, charge_point_identify: str):
        global active_connection
        await websocket.accept(subprotocol='ocpp1.6')

        ch_p = ChargePoint(charge_point_identify, websocket)
        await ch_p.start()
        active_connection[charge_point_identify] = ch_p

    def disconnect(self, websocket: WebSocket):


    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket_route("ws/{charge_point_identify}")
async def websocket_endpoint(websocket: WebSocket, charge_point_identify: str):
    await manager.connect(websocket, charge_point_identify)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
