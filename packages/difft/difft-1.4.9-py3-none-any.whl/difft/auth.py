import collections
import hashlib
import hmac
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests

from difft import constants
from difft.utils import current_milli_time, get_nonce


class Signature:
    def __init__(self, timestamp: int, nonce: str, algorithm: str, signature: str) -> None:
        self.timestamp = timestamp
        self.nonce = nonce
        self.algorithm = algorithm
        self.signature = signature


class Authenticator(requests.auth.AuthBase):
    def __init__(self, appid: str, key: bytes, headers: Optional[list] = None) -> None:
        self._appid = appid
        self._key = key
        if headers:
            headers.append("Content-Type")
            headers.append("Content-Length")
        else:
            headers = ["Content-Type", "Content-Length"]
        self._headerToSign = headers

    def __call__(self, r):
        method = r.method

        parsed_url = urlparse(r.url)

        uri = parsed_url.path
        query_parameters = parse_qs(parsed_url.query,keep_blank_values=True)
        sorted_query_parameters = collections.OrderedDict(sorted(query_parameters.items()))

        headers = r.headers
        headerToSign = {}
        headerToSignList = []
        for k in headers:
            if k in self._headerToSign:
                headerToSign[k] = headers[k]
                headerToSignList.append(k)

        headerToSignStr = ",".join(headerToSignList)

        sorted_headers = collections.OrderedDict(sorted(headerToSign.items()))

        body = r.body

        dataToSign = self.build_data(method, uri, sorted_query_parameters, sorted_headers, body)
        signature = self.sign(dataToSign)
        new_headers = {
            constants.HEADER_NAME_APPID: self._appid,
            constants.HEADER_NAME_TIMESTAMP: signature.timestamp,
            constants.HEADER_NAME_NONCE: signature.nonce,
            constants.HEADER_NAME_ALGORITHM: signature.algorithm,
            constants.HEADER_NAME_SIGNEDHEADERS: headerToSignStr,
            constants.HEADER_NAME_SIGNATURE: signature.signature,
        }
        r.headers.update(new_headers)
        return r

    def build_data(
        self, method: str, uri: str, parameters: dict, headers: dict, body: Optional[bytes]
    ) -> bytes:
        data = method + ";" + uri + ";"
        for k in parameters:
            for i in parameters[k]:
                data += k + "=" + i + ","
        data = data[:-1]
        data += ";"

        for k in headers:
            data += k.lower() + "=" + headers[k] + ","

        data = data[:-1]
        data += ";"
        data = data.encode("utf-8")
        if body:
            data += body

        return data

    def sign(self, msg: bytes) -> Signature:
        ts = current_milli_time()
        nonce = get_nonce()
        data = ";".join([self._appid, str(ts), nonce]) + ";"
        msg = data.encode("utf-8") + msg
        sign_str = hmac.new(self._key, msg, hashlib.sha256).hexdigest()
        return Signature(
            timestamp=ts, nonce=nonce, algorithm=constants.ALGORITHM_HMAC_SHA256, signature=sign_str
        )
