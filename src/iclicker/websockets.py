import websocket
import rel
import json
from .request import POST, GET, gen_headers
import logging

logger = logging.getLogger(__name__)

uid: str | None = None
auth: str | None = None
course_id: str | None = None
activity_id: str | None = None

def on_open(_: websocket.WebSocket):
    logger.debug("Opened connection")
    return

def on_message(ws: websocket.WebSocket, message: str):
    evt: dict = json.loads(message)
    data = json.loads(evt["data"])
    if evt["event"] != "answer" and evt["event"] != "pusher:connection_established":
        return

    if evt["event"] == "answer":
        # question answering logic (not working yet, because registering userQuestionId is needed)
        question_id = data["questionId"]
        # question_name = data["name"]
        # activity_id = data["activityId"]
        # logger.info(f"Answering {question_name}")

        global uid
        global auth
        global activity_id
        auth_header = f"Bearer {auth}"
        answer_headers = gen_headers(content_type="application/json", auth=auth_header)
        resp = POST(f"https://api.iclicker.com/v2/activities/{activity_id}/questions/{question_id}/user-questions/",
                          { "activityId": activity_id, "answer": "a", "clientType": "WEB", "questionId": question_id, "userId": uid },
                          answer_headers)
        logger.info(resp.text)
        # probably use the above data excluding answer and hit "https://api.iclicker.com/v1/userQuestions"
        # it will likely return something useful
        # assuming no validation occurs more data better than less
        # then hit the question answerer (append user question id to end of url) with above payload + answer
    else:
        # websocket authentication logic
        socket_id = data["socket_id"]
        auth_val = f"Bearer {auth}"
        course_channel_name = f"private-{course_id}"
        user_channel_name = f"private-{course_id}@{uid}"
        auth_headers = gen_headers(content_type="application/x-www-form-urlencoded", auth=auth_val)
        course_auth_response = POST("https://api.iclicker.com/v1/websockets/authenticate-pusher-channel",
                                    None, text=f"socket_id={socket_id}&channel_name={course_channel_name}", headers=auth_headers)
        course_auth = course_auth_response.json()["auth"]
        user_auth_response = POST("https://api.iclicker.com/v1/websockets/authenticate-pusher-channel",
                                  None, text=f"socket_id={socket_id}&channel_name={user_channel_name}", headers=auth_headers)
        user_auth = user_auth_response.json()["auth"]

        course_sub = {
                "event": "pusher:subscribe",
                "data": {
                    "auth": course_auth,
                    "channel": course_channel_name
                }
        }
        user_sub = {
                "event": "pusher:subscribe",
                "data": {
                    "auth": user_auth,
                    "channel": user_channel_name
                }
        }

        logger.debug(course_sub)
        logger.debug(user_sub)

        ws.send(json.dumps(course_sub))
        ws.send(json.dumps(user_sub))

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
    global course_id
    global activity_id
    auth = auth_token
    uid = user_id
    course_id = keys["course_id"]
    headers = gen_headers("application/json", f"Bearer {auth}")
    resp = GET(f"https://api.iclicker.com/v2/courses/{course_id}/class-sections?expandChild=activities&userId={uid}",
                None, headers)
    activity_id = resp.json()[0]["activities"][0]["_id"]
    logger.info(f"Activity id: {activity_id}")
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(f"wss://ws-mt1.pusher.com/app/{ws_key}?protocol=7&client=js&version=8.3.0&flash=false",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(dispatcher=rel, reconnect=5, ping_interval=120, ping_timeout=10, ping_payload='{"event":"pusher:pong","data":"{}"}')
    rel.signal(2, rel.abort)
    rel.dispatch()
