from http import HTTPStatus
from typing import Optional, List
from starlette.websockets import WebSocket

from exceptions import AuthError, InvalidTokenError, WebsocketConnectError


class UserConnection:
    def __init__(self, websocket: WebSocket, token: str, subscriptions: Optional[list] = None):
        self.websocket = websocket
        self.token = token
        self.subscriptions = subscriptions

    def __dict__(self):
        return {
            'websocket_state': self.websocket.client_state,
            'token': self.token,
            'subscriptions': self.subscriptions
        }

    async def send(self, data):
        await self.websocket.send_json(data)

    async def receive(self):
        await self.websocket.receive()


class UserConnectionManager:
    def __init__(self):
        self.active_connections: List[UserConnection] = []

    @staticmethod
    def _get_token_value_from_header(auth_header: str) -> str:
        constituents = auth_header.split(' ')
        if len(constituents) != 2 or constituents[0] != 'Token':
            raise InvalidTokenError('Invalid token')

        return constituents[1]

    def _get_subscriptions_from_request(self, websocket: WebSocket) -> Optional[List[str]]:
        subscriptions_string: str = websocket.query_params.get('subscriptions', None)

        if subscriptions_string is None:
            return None

        try:
            subscriptions = subscriptions_string.split(',')
            return subscriptions

        except (ValueError, TypeError):
            raise WebsocketConnectError(status_code=HTTPStatus.BAD_REQUEST, detail='invalid subscriptions data')

    def get_user_by_token(self, token: str) -> Optional[UserConnection]:
        for user in self.active_connections:
            if user.token == token:
                return user
        return None

    def get_user_by_websocket(self, websocket: WebSocket) -> Optional[UserConnection]:
        for user in self.active_connections:
            if user.websocket == websocket:
                return user
        return None

    def get_users_by_subscribes(self, event: str) -> List[UserConnection]:
        users = list()

        for user in self.active_connections:
            if user.subscriptions and event in user.subscriptions:
                users.append(user)
        return users

    async def connect(self, websocket: WebSocket) -> UserConnection:
        await websocket.accept()
        auth_header = websocket.headers.get('Authorization', None)
        if auth_header is None:
            raise AuthError('Not Authenticated', status_code=HTTPStatus.NOT_FOUND)

        token = self._get_token_value_from_header(auth_header)

        for connection in self.active_connections:
            if connection.token == token:
                raise AuthError('User already connected')

        subscriptions = self._get_subscriptions_from_request(websocket)

        user = UserConnection(websocket, token, subscriptions)
        self.active_connections.append(user)
        return user

    def disconnect(self, user: UserConnection):
        self.active_connections.remove(user)

    async def send_personal_message(self, message: dict, user: UserConnection):
        await user.send(message)

    async def broadcast(self, message: dict, users: List[UserConnection] = None):
        if users is None:
            for user in self.active_connections:
                await user.send(message)
            return

        for user in users:
            await user.send(message)

