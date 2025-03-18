import websocket
import rel
import json
from .request import POST, gen_headers
import logging

logger = logging.getLogger(__name__)

uid: str | None = None
auth: str | None = None

def on_open(_: websocket.WebSocket):
    logger.debug("Opened connection")
    return

def on_message(_: websocket.WebSocket, message: str):
    evt: dict = json.loads(message)
    if evt["event"] != "question":
        return
    question_id = evt["data"]["questionId"]
    question_name = evt["data"]["name"]
    activity_id = evt["data"]["activityId"]
    logger.info(f"Answering {question_name}")

    global uid
    global auth
    auth_header = f"Bearer {auth}"
    answer_headers = gen_headers(content_type="application/json", auth=auth_header)
    __ = POST("https://api.iclicker.com/v2/activities/{activity_id}/questions/{question_id}/user-questions/",
                      { "activityId": activity_id, "answer": "a", "clientType": "WEB", "questionId": question_id, "user_id": uid },
                      answer_headers)

    logger.debug(message)

def on_error(_: websocket.WebSocket, error: str):
    logger.error(error)

def on_close(_: websocket.WebSocket, code: int, message: str):
    logger.debug(f"Closed connection with code {code} and message {message}")

def connect(keys: dict[str, str]):
    ws_key = keys["ws_key"]
    user_id = keys["user_id"]
    auth_token = keys["auth_token"]
    global auth
    global uid
    auth = auth_token
    uid = user_id
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"wss://ws-mt1.pusher.com/app/{ws_key}?protocol=7&client=js&version=8.3.0&flash=false",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(dispatcher=rel, reconnect=5, ping_interval=120, ping_timeout=10, ping_payload='{"event":"pusher:pong","data":"{}"}')
    rel.signal(2, rel.abort)
    rel.dispatch()
