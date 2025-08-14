class AttachmentBuilder:
    def __init__(self) -> None:
        self._attachment = dict(contentType="text/html")

    def authorize_id(self, authorize_id):
        self._attachment["authorizeId"] = authorize_id
        return self

    def key(self, key):
        self._attachment["key"] = key
        return self

    def file_size(self, file_size):
        self._attachment["size"] = file_size
        return self

    def file_name(self, file_name):
        self._attachment["fileName"] = file_name
        return self

    def digest(self, cipher_hash):
        self._attachment["digest"] = cipher_hash
        return self

    def content_type(self, content_type):
        self._attachment["contentType"] = content_type
        return self

    def flags(self, flags):
        self._attachment["flags"] = flags
        return self

    def width(self, width):
        self._attachment["width"] = width
        return self

    def height(self, height):
        self._attachment["height"] = height
        return self

    def preview(self, preview):
        self._attachment["preview"] = preview
        return self

    def caption(self, caption):
        self._attachment["caption"] = caption
        return self

    def url(self, url):
        self._attachment["url"] = url
        return self

    def build(self):
        return self._attachment
