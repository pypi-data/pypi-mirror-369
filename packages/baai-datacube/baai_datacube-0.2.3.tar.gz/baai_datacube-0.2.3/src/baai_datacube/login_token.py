import json
import base64
import requests

from pydantic import BaseModel

from .config import Application


class JwtClaims(BaseModel):
    sub : str
    iat : int
    exp : int


def claims_parse(jwt_token):
    parts = jwt_token.split('.')
    if len(parts) != 3:
        return None
    payload = parts[1]

    padding = 4 - len(payload) % 4
    if padding != 4:
        payload += '=' * padding

    decoded_bytes = base64.b64decode(payload)
    decoded_str = decoded_bytes.decode('utf-8')
    return json.loads(decoded_str)

