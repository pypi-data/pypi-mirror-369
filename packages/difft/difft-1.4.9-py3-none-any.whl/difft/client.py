import base64
import hashlib
import json
import logging
import os

import requests

from difft import constants
from difft.auth import Authenticator
from difft.crypto import decrypt_attachment, encrypt_attachment
from difft.utils import parse_response


class DifftClient:
    """Main class wrapper around Wea methods.

    Wraps authentication logic as well as some more complex workflows like
    sendin medias.

    """

    # arbitrary that's high enough given my ignorance of the difft server, but
    # small enough most API won't significantly break if we hit it
    # not applied on media requests.
    REQUEST_TIMEOUT = 5

    def __init__(self, appid: str, key: str, host: str = "https://openapi.test.difft.org"):
        self._auth = Authenticator(appid, key.encode("utf-8"))
        self._host = host

    def upload_attachment(
        self, send_wuid: str, group_ids: list, acceptor_wuid: list, attachment: bytes
    ) -> dict:
        """Upload attachment to oss storage.

        :param send_wuid: bot wuid
        :param group_ids: list of group id
        :param acceptor_wuid: list of acceptor wuid
        :param attachment: bytes of attachment

        :return: map of authorizeId, key, cipherHash, fileSize
        """
        key = hashlib.sha512(attachment).digest()
        fileHash = hashlib.sha256(key).digest()
        fileSize = len(attachment)
        is_exist_body = dict(
            wuid=send_wuid,
            fileHash=base64.b64encode(fileHash).decode("utf-8"),
            fileSize=fileSize,
            gids=group_ids,
            numbers=acceptor_wuid,
        )
        is_exist_resp = requests.post(
            url=self._host + constants.URL_ISEXIST,
            json=is_exist_body,
            auth=self._auth,
        )

        is_exist_resp_obj = json.loads(is_exist_resp.text)
        if is_exist_resp_obj.get("status") != 0:
            raise Exception(is_exist_resp_obj.get("reason"))

        data = is_exist_resp_obj.get("data")
        if data.get("exists"):
            # file already exist, skip upload
            return dict(
                authorizeId=data.get("authorizeId"),
                key=base64.b64encode(key).decode("utf-8"),
                cipherHash=data.get("cipherHash"),
                fileSize=fileSize,
            )

        # upload attachment to oss
        ciphertext = encrypt_attachment(attachment, key)
        cipherHash = hashlib.md5(ciphertext).hexdigest()
        requests.put(data.get("url"), data=ciphertext)

        upload_info = dict(
            wuid=send_wuid,
            fileHash=base64.b64encode(fileHash).decode("utf-8"),
            attachmentId=data.get("attachmentId"),
            fileSize=fileSize,
            hashAlg="SHA256",
            keyAlg="SHA512",
            encAlg="AES-CBC-SHA256",
            cipherHash=cipherHash,
            cipherHashType="MD5",
            gids=group_ids,
            numbers=acceptor_wuid,
        )
        # report uploadinfo to server
        upload_info_resp = requests.post(
            url=self._host + constants.URL_UPLOAD_ATTACHMENT, json=upload_info, auth=self._auth
        )
        upload_info_resp_obj = json.loads(upload_info_resp.text)
        if upload_info_resp_obj.get("status") != 0:
            raise Exception(upload_info_resp_obj.get("reason"))
        data = upload_info_resp_obj.get("data")
        return dict(
            authorizeId=data.get("authorizeId"),
            key=base64.b64encode(key).decode("utf-8"),
            cipherHash=cipherHash,
            fileSize=fileSize,
        )

    def download_attachment(self, wuid, key, authorize_id, cipher_hash, url=None) -> bytes:
        """Download attachment from oss.

        :param wuid: bot id
        :param key:
        :param authorize_id:
        :param cipher_hash:
        :param url: attachment download link if existed, default None

        :return: plain attachment, bytes
        """
        key = base64.b64decode(key)
        if not url:
            fileHash = hashlib.sha256(key).digest()
            download_attachment_body = dict(
                wuid=wuid,
                fileHash=base64.b64encode(fileHash).decode("utf-8"),
                authorizeId=authorize_id,
            )
            download_attachment_resp = requests.post(
                url=self._host + constants.URL_DOWNLOAD_ATTACHMENT,
                json=download_attachment_body,
                auth=self._auth,
            )
            download_attachment_obj = json.loads(download_attachment_resp.text)
            if download_attachment_obj.get("status") != 0:
                raise Exception(download_attachment_obj.get("reason"))
            data = download_attachment_obj.get("data")
            url = data.get("url")
        attachment_resp = requests.get(url=url)
        attachment = attachment_resp.content

        return decrypt_attachment(attachment, key, bytes.fromhex(cipher_hash))

    def append_attachment_authorization(self, wuid, fil_hash, file_size, group_ids, acceptor_wuid):
        """Append user authorization to existed attachment.

        :param wuid: bot id
        :param fil_hash:
        :param file_size:
        :param group_ids:
        :param acceptor_wuid:

        :return: authorizeId if success, otherwise raise exception
        """
        is_exist_body = dict(
            wuid=wuid, fileHash=fil_hash, fileSize=file_size, gids=group_ids, numbers=acceptor_wuid
        )
        is_exist_resp = requests.post(
            url=self._host + constants.URL_ISEXIST, json=is_exist_body, auth=self._auth
        )
        is_exist_resp_obj = json.loads(is_exist_resp.text)
        if is_exist_resp_obj.get("status") != 0:
            raise Exception(is_exist_resp_obj.get("reason"))

        data = is_exist_resp_obj.get("data")
        if not data.get("exists"):
            raise Exception("file not exist")

        return data.get("authorizeId")

    def delete_attachment_authorization(self, wuid, filehash, authorizeIds):
        """Delete specific authorization by authorizeIds,

        :param wuid:
        :param filehash:
        :param authorizeIds:

        :return: True if success
        """
        delete_attachment_auth_body = dict(
            wuid=wuid, delAuthorizeInfos=[dict(fileHash=filehash, authorizeIds=authorizeIds)]
        )
        delete_attachment_auth_resp = requests.post(
            url=self._host + constants.URL_DEL_ATTACHMENT,
            json=delete_attachment_auth_body,
            auth=self._auth,
        )
        delete_attachment_auth_obj = json.loads(delete_attachment_auth_resp.text)
        if delete_attachment_auth_obj.get("status") != 0:
            logging.error(delete_attachment_auth_obj.get("reason"))
            return False
        return True

    def upload_pic(self, picture_path, raw_response=False):
        """Upload picture so we can refer to it within messages.

        :param picture_path: any filename
        :return: online image url
                 {
                      "ver": 1,
                      "status": 0,
                      "reason": "success",
                      "data": {
                        "url": "https://difft-oss.s3.ap-southeast-1.amazonaws.com/50ab44ae13bf26337a1c1d3a0cdcc53c?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIASJTLN2W46QBZ6M65%2F20221122%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Date=20221122T113605Z&X-Amz-Expires=300&X-Amz-SignedHeaders=host&x-id=GetObject&X-Amz-Signature=84ee194a240902561a749626d0eaa690cce885e5bc1056fd0ee1a70d8313a35d"
                      }
                 }
        """
        if not os.path.exists(picture_path):
            raise Exception("file %s not found" % picture_path)

        filename = os.path.basename(picture_path)

        with open(picture_path, "rb") as fd:
            content = base64.b64encode(fd.read())

        payload = {
            'file_name': filename,
            # make it serializable to json
            'content': content.decode('utf-8'),
        }
        res = requests.post(
            url=self._host + constants.URL_UPLOAD_PIC, json=payload, auth=self._auth
        )
        if res.status_code != 200:
            raise Exception("failed to upload image, server responded with %d" % res.status_code)
        envelope = res.json()
        if envelope.get("status") != 0:
            raise Exception("pic upload failed", envelope.get("errors"), envelope.get("error"))

        # done managing error cases, send back data
        if raw_response:
            return envelope
        else:
            return envelope.get("data").get("url")

    def send_message(self, msg, raw_response=False):
        """Send message.

        :param msg: MessageRequest
        :param raw_response: whether to get raw response or not

        :return: list of fail reason,
                [
                    {
                    "wuid":"idxxx",
                    "groupID":"{wea group id}",
                    "reason":"failed reason"
                    }
                ]
                raw response:
                {
                    "status":0, // 0 表示成功，否则为失败
                    "errors":[{
                        "wuid":"idxxx",
                        "groupID":"{wea group id}",
                        "reason":"failed reason"
                    }],
                    "refID":"v1:1649814691000:+800000000" // 当消息可被引用时，返回该消息的refID
                }
        """
        send_msg_resp = requests.post(
            url=self._host + constants.URL_SEND_MSG,
            json=msg,
            auth=self._auth,
            timeout=self.REQUEST_TIMEOUT,
        )
        if send_msg_resp.status_code != 200:
            raise Exception("server response %d" % send_msg_resp.status_code)
        send_msg_resp_obj = json.loads(send_msg_resp.text)
        if send_msg_resp_obj.get("status") != 0:
            raise Exception(
                "send message failed",
                send_msg_resp_obj.get("errors"),
                send_msg_resp_obj.get("error"),
            )
        if raw_response:
            return send_msg_resp_obj
        else:
            return send_msg_resp_obj.get("errors")

    def get_account_by_email(self, email):
        param = dict(email=email)
        return self.get_account(param)

    def get_account_by_wuid(self, wuid, operator):
        # see https://git.toolsfdg.net/difftim/difft-sdk-python/issues/8
        # unlike retrieval by email, it seems retrieval by wuid requires to
        # specify the operator (i.e. the bot id)
        param = dict(wuid=wuid, operator=operator)
        return self.get_account(param)

    def get_account(self, params):
        resp = requests.get(
            url=self._host + constants.URL_ACCOUNT,
            params=params,
            auth=self._auth,
            timeout=self.REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            raise Exception("server response error, code", resp.status_code)
        resp_obj = json.loads(resp.text)
        if resp_obj.get("status") != 0:
            raise Exception(resp_obj.get("reason"))
        return resp_obj.get("data")

    def create_group(self, payload):
        resp = requests.post(
            url=self._host + constants.URL_GROUP,
            json=payload,
            auth=self._auth,
            timeout=self.REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            raise Exception("server response error, code", resp.status_code)
        resp_obj = json.loads(resp.text)
        if resp_obj.get("status") != 0:
            raise Exception(resp_obj.get("reason"))
        return resp_obj.get("data")

    def add_members(self, gid, operator, accounts):
        payload = {'gid': gid, 'operator': operator, 'accounts': accounts}
        resp = requests.put(
            url=self._host + constants.URL_ADD_MEMBERS,
            json=payload,
            auth=self._auth,
            timeout=self.REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            raise Exception("server response error, code", resp.status_code)
        resp_obj = json.loads(resp.text)
        if resp_obj.get("status") != 0:
            raise Exception(resp_obj.get("reason"))
        return resp_obj.get("data")

    def get_group_by_botid(self, botid):
        params = dict(operator=botid)
        resp = requests.get(
            url=self._host + constants.URL_GROUP,
            params=params,
            auth=self._auth,
            timeout=self.REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            raise Exception("server response error, code", resp.status_code)
        resp_obj = json.loads(resp.text)
        if resp_obj.get("status") != 0:
            raise Exception(resp_obj.get("reason"))
        if "groups" in resp_obj.get("data"):
            return resp_obj.get("data").get("groups")
        return []

    @parse_response
    def get_group_members(self, botid, gid):
        """Fetch group members.

        API: https://documenter.getpostman.com/view/14311359/UVREmkXq#8953dbf9-1fb7-486b-81a5-1b58938218d9

        """
        params = dict(operator=botid, gid=gid)
        return requests.get(
            url=self._host + constants.URL_GROUP_MEMBERS,
            params=params,
            auth=self._auth,
            timeout=self.REQUEST_TIMEOUT,
        )
