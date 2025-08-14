import json
import random
import time
import uuid

HTTP_OK = 200
SERVER_STATUS_OK = 0
LETTERS = "abcdefghijklmnopqrstuvwxyz0123456789"


def random_str(n: int):
    return ''.join(random.choice(LETTERS) for _ in range(n))


def get_nonce():
    new_uuid = uuid.uuid4()
    return new_uuid.hex


def current_milli_time():
    return round(time.time() * 1000)


def parse_response(func):
    """Decorator to parse standard Difft server response.

    Note that if nothing bad is detected, it will return response['data'], and
    assume json response. While this seems to be the expected behaviour
    across the board, it means the caller needs to know how to access the
    underlying data (i.e. instead of getting a list of members, one need gets
    it through resp.get['members']).

    But we think this can be easily documented, provide more standard, less
    boilerplate, and anyway expose the initial server response payload.

    One downside though is that if moving to a more typed python, the function
    and the decorator will be poorly informative, and may justidy a different
    approach. But at this stage this seems to be the most productive.

    """

    def __inner(*args, **kwargs):
        # api call
        resp = func(*args, **kwargs)

        if resp.status_code != HTTP_OK:
            raise Exception("server response error, code", resp.status_code, resp.text)

        resp_obj = json.loads(resp.text)

        if resp_obj.get("status") != SERVER_STATUS_OK:
            raise Exception(resp_obj.get("reason"))

        return resp_obj.get("data")

    return __inner
