from http import HTTPStatus

from fastapi import APIRouter
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from DTO import NotificationPrivateDTO, NotificationBroadcastDTO, NotificationEventDTO
from exceptions import WebsocketConnectError
from services import UserConnectionManager

manager = UserConnectionManager()

root = APIRouter(prefix='/api/notifications')


@root.post('/private')
async def private_notification(data: NotificationPrivateDTO):
    user = manager.get_user_by_token(data.token)
    if user is None:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND)

    await manager.send_personal_message(data.notification, user)
    return JSONResponse(status_code=HTTPStatus.OK)


@root.post('/broadcast')
async def broadcast_notification(data: NotificationBroadcastDTO):
    await manager.broadcast(data.notification)
    return JSONResponse(HTTPStatus.OK)


@root.post('/event')
async def event_notification(data: NotificationEventDTO):
    users = manager.get_users_by_subscribes(data.event)
    await manager.broadcast(data.notification, users=users)
    return JSONResponse(HTTPStatus.OK)


@root.websocket('/notifications')
async def websocket_root(websocket: WebSocket):
    try:
        user = await manager.connect(websocket)
    except WebsocketConnectError as err:
        await websocket.send_json({'detail': err.detail, 'status': err.status_code})
        await websocket.close()
        return

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user)
