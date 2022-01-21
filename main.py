from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from controllers import root

app = FastAPI()

app.include_router(root)

