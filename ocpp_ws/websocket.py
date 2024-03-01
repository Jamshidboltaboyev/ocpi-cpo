import asyncio
import os
import websockets
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zty.settings")
get_asgi_application()

from utilss import CommandParser, PubSub
from charge_point import ChargePoint

active_connection = {}


class OcppWebSocketServerProtocol:
    async def on_connect(self, websocket, path: str):
        global active_connection
        connection_id = path.split('/')[-1]
        cp = ChargePoint(connection_id, websocket)
        active_connection[connection_id] = cp
        await cp.start()

    async def subscribe_to_pubsub(self):
        global active_connection
        channel_name = 'events'
        while True:
            try:
                value = await PubSub().subscribe(channel_name)
                command: CommandParser = CommandParser.parse_raw(value)

                if command.charge_point_id not in active_connection:
                    continue
                cp: ChargePoint = active_connection[command.charge_point_id]
                mapping = {
                    "RemoteStartTransaction": cp.send_remote_start_transaction_command,
                    "RemoteStopTransaction": cp.send_remote_stop_transaction_command
                }
                await mapping[command.command](**command.kwargs)
            except Exception as e:
                pass

    async def start_server(self):
        port = 49000
        print("running on: ", port)
        server = await websockets.serve(self.on_connect, host='0.0.0.0', port=port, subprotocols=['ocpp1.6'])
        await server.wait_closed()

    async def start(self):
        await asyncio.gather(self.start_server(), self.subscribe_to_pubsub())


asyncio.run(OcppWebSocketServerProtocol().start())
