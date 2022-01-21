from pydantic import BaseModel


class NotificationBroadcastDTO(BaseModel):
    notification: dict


class NotificationPrivateDTO(BaseModel):
    token: str
    notification: dict


class NotificationEventDTO(BaseModel):
    event: str
    notification: dict
