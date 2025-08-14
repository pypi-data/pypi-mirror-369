import json
import logging
import time

import rel
import websocket

from difft import constants
from difft.auth import Authenticator

class DifftWsListener:
    RECONNECT_DELAY = 15
    PING_INTERVAL = 30
    PING_TIMEOUT = 5

    def __init__(self, appid, key, domain="openapi.test.difft.org") -> None:
        if not isinstance(appid, str):
            raise Exception("appid should be type str")
        if not isinstance(key, str):
            raise Exception("key should be type str")

        self._appid = appid
        self.auth = Authenticator(appid=appid, key=key.encode("utf-8"))
        self.domain = domain

    def handler(self, handler):
        self.message_handler = handler

    def start(self):
        dataToSig = self.auth.build_data("GET", "/v1/websocket", {}, {}, None)
        signature = self.auth.sign(dataToSig)
        auth_headers = {
            constants.HEADER_NAME_APPID: self._appid,
            constants.HEADER_NAME_TIMESTAMP: signature.timestamp,
            constants.HEADER_NAME_NONCE: signature.nonce,
            constants.HEADER_NAME_ALGORITHM: signature.algorithm,
            constants.HEADER_NAME_SIGNEDHEADERS: "",
            constants.HEADER_NAME_SIGNATURE: signature.signature,
        }
        headers = []
        for k in auth_headers:
            headers.append("{}:{}".format(k, auth_headers[k]))
        url = "wss://{}/v1/websocket".format(self.domain)

        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    url,
                    header=headers,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_pong=self.on_pong,
                )

                rel.init()
                # ping interval is 30 second
                self.ws.run_forever(ping_interval=self.PING_INTERVAL, dispatcher=rel, ping_timeout=self.PING_TIMEOUT)
                self.fetch(self.ws)

                rel.signal(2, rel.abort)  # Keyboard Interrupt
                rel.dispatch()
            except Exception as e:
                logging.error(
                    "[DifftWsListener] got error: {}, my appid: {}".format(e, self._appid)
                )
                logging.info("[DifftWsListener] will retry in {} seconds".format(self.RECONNECT_DELAY))
                time.sleep(self.RECONNECT_DELAY)

    def on_message(self, ws, message):
        logging.debug("[DifftWsListener] receive data: {}".format(message))
        try:
            obj = json.loads(message)
            for data in obj.get("messages", []):
                if "data" in data:
                    self.message_handler(data["data"])
        except Exception as e:
            logging.error("[DifftWsListener] handle message failed, error: {}".format(e))
        self.fetch(ws)

    def on_error(self, ws, error):
        logging.error(
            "[DifftWsListener] websocket error {}, my appid: {}".format(error, self._appid)
        )
        self.ws.close()
        rel.abort()

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(
            "[DifftWsListener] on_close, code {}, reason {}".format(close_status_code, close_msg)
        )
        if close_status_code == 1008:
            logging.warn("[DifftWsListener] close code is 1008, stop listening")
            rel.abort()
        else:
            logging.info("[DifftWsListener] on_close, will retry connection later")
            self.ws.close()
            rel.abort()

    def on_open(self, ws):
        logging.info("[DifftWsListener] websocket connected")

    def on_pong(self, ws, msg):
        logging.debug("[DifftWsListener] got pong response, my appid: {}".format(self._appid))

    def fetch(self, ws):
        ws.send('{"cmd":"fetch"}')

    def close(self):
        self.ws.send('{"cmd":"commit"}')
        rel.abort()
        self.ws.close()
