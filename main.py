from http import HTTPStatus
from fastapi import FastAPI, Request
from starlette.responses import Response

import settings
from controllers import root

app = FastAPI()


@app.middleware('http')
async def check_api_key(request: Request, call_next):
    api_key = request.headers.get('api_key', None)
    if not api_key:
        return Response('No api_key specified', status_code=HTTPStatus.BAD_REQUEST)
    if api_key != settings.API_KEY:
        return Response('Invalid api_key', status_code=HTTPStatus.BAD_REQUEST)

    response = await call_next(request)
    return response

app.include_router(root)

