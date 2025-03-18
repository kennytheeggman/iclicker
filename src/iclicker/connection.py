from .request import gen_headers, POST, GET
from types import NoneType
from typing import Callable
import time
import logging

logger = logging.getLogger(__name__)

def validate(email: str):
    logger.info("Validating email")
    validation_headers = gen_headers(content_type="application/json")
    validation_res = POST("https://api.iclicker.com/trogon/v1/federation/account/validate",
               { "email": email }, validation_headers)
    return validation_res

def login(email: str, password: str):
    logger.info("Logging in")
    login_headers = gen_headers(content_type="application/vnd.reef.login-proxy-request-v1+json")
    login_res = POST("https://api.iclicker.com/authproxy/login",
                     { "email": email, "password": password }, 
                     login_headers)
    return login_res

def profile(token: str):
    logger.info("Getting profile")
    auth = f"Bearer {token}"
    profile_headers = gen_headers(content_type="application/json", auth=auth)
    profile_res = GET("https://api.iclicker.com/trogon/v4/profile", None, profile_headers);
    return profile_res

def user_courses(user_id: str, token: str):
    logger.info("Getting courses")
    auth = f"Bearer {token}"
    course_headers = gen_headers(content_type="application/json", auth=auth)
    course_res = GET(f"https://api.iclicker.com/v1/users/{user_id}/views/student-courses", None, course_headers)
    return course_res

def status(course_id: str, token: str):
    logger.debug("Getting status")
    auth = f"Bearer {token}"
    status_headers = gen_headers(content_type="application/vnd.reef.student-course-status-request-v1+json", auth=auth)
    status_res = POST("https://api.iclicker.com/student/course/status", 
                     { "courseId": course_id }, status_headers)
    return status_res

def join(enrollment_id: str, meeting_id: str, token: str):
    logger.info("Joining class")
    auth = f"Bearer {token}"
    join_headers = gen_headers(content_type="application/json", auth=auth)
    join_res = POST(f"https://api.iclicker.com/v1/meetings/{meeting_id}/join-participant", 
                    { "enrollmentId": enrollment_id, "meetingId": meeting_id }, join_headers)
    return join_res

def wskey(token: str):
    logger.debug("Getting websocket key")
    auth = f"Bearer {token}"
    ws_headers = gen_headers(content_type="application/json", auth=auth)
    ws_res = GET(f"https://api.iclicker.com/v1/settings/pusher-cluster-primary/value", None, ws_headers)
    return ws_res

def connect(user: str, password: str, waits: list[Callable[[], NoneType]], getcourse: Callable[[], int], status_interval: int):
    validation_res = validate(user)
    login_res = login(user, password)
    institution_id = validation_res.json()["institutionId"]
    institution_name = validation_res.json()["institutionName"]
    auth_token = login_res.json()["access_token"]
    logger.debug(f"Authorization token: {auth_token}")
    
    profile_res = profile(auth_token)
    profile_json = profile_res.json()
    user_id = profile_json["userid"]
    first_name = profile_json["firstName"]
    last_name = profile_json["lastName"]
    email = profile_json["email"]
    student_id = profile_json["studentId"]
    sec_key = profile_json["seckey"] 
    num_courses = profile_json["courseCount"]
    logger.info(f"Name: {first_name} {last_name}")
    logger.info(f"Email: {email}")
    logger.info(f"Student Id: {student_id}")
    logger.info(f"Institution: {institution_name}")
    logger.debug(f"User Id: {user_id}")
    logger.debug(f"Institution Id: {institution_id}")
    logger.debug(f"Security Key: {sec_key}")
    logger.debug(f"Course Count: {num_courses}")

    course_res = user_courses(user_id, auth_token)
    courses: list = course_res.json()["enrollments"]
    for idx, course in enumerate(courses):
        enrollment_id = course["enrollmentId"]
        course_id = course["courseId"]
        name = course["name"]
        instructors = course["instructors"]
        logger.debug(f"Enrollment Id: {enrollment_id}")
        logger.debug(f"Course Id: {course_id}")
        logger.info(f"{idx}: {name} {', '.join(instructors)}")

    selected = getcourse() 
    course = courses[selected]
    enrollment_id = course["enrollmentId"]
    course_id = course["courseId"]
    name = course["name"]
    instructors = course["instructors"]

    waits[0]()
    while (status(course_id, auth_token).json()["meetingId"] is None):
        try:
            time.sleep(status_interval)
        except KeyboardInterrupt:
            logger.info("Stopping Connection")
            exit(0)
    waits[1]()

    status_res = status(course_id, auth_token)
    meeting_id = status_res.json()["meetingId"]
    logger.debug(f"Meeting Id: {meeting_id}")

    join_res = join(enrollment_id, meeting_id, auth_token)
    join_json = join_res.json()
    participant_id = join_json["participantId"]
    logger.debug(f"Participant Id: {participant_id}")

    ws_res = wskey(auth_token)
    cluster = ws_res.json()["cluster"]
    ws_key = ws_res.json()["key"]
    logger.debug(f"Cluster: {cluster}")
    logger.debug(f"Websocket key: {ws_key}")

    ret_dict = {
        "auth_token": auth_token,
        "user_id": user_id,
        "enrollment_id": enrollment_id,
        "course_id": course_id,
        "meeting_id": meeting_id,
        "participant_id": participant_id,
        "ws_key": ws_key
    }

    return ret_dict

