import hashlib
import hmac

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

PAD5_BLOCK_SIZE = 16


def pkcs5_pad(s: bytes, encoding='utf8') -> bytes:
    """Padding to blocksize according to PKCS #5.

    Calculates the number of missing chars to BLOCK_SIZE and pads with
    ord(number of missing chars).
    """
    padded = PAD5_BLOCK_SIZE - len(s) % PAD5_BLOCK_SIZE
    return s + padded * chr(padded).encode(encoding)


def pkcs5_unpad(s: bytes) -> bytes:
    """Unpadding according to PKCS #5."""
    return s[0 : -s[-1]]


def hmac_sha256(keys, iv, ciphertext):
    digest = hmac.new(keys, iv + ciphertext, hashlib.sha256).digest()
    return digest


def encrypt_attachment(attachment, key):
    if len(key) != 64:
        raise Exception("got invalid length keys (%d bytes)" % len(key))

    iv = get_random_bytes(16)
    cipher = AES.new(key[:32], AES.MODE_CBC, iv)
    attachment_cipher = cipher.encrypt(pkcs5_pad(attachment))
    mac = hmac_sha256(key[32:], iv, attachment_cipher)
    ciphertext = iv + attachment_cipher + mac

    return ciphertext


def decrypt_attachment(ciphertext, keys, thier_digest) -> bytes:
    if len(keys) != 64:
        raise Exception("got invalid length keys")

    ciphertext_length = len(ciphertext)
    iv = ciphertext[:16]
    mac = ciphertext[ciphertext_length - 32 :]
    attachment_cipher = ciphertext[16 : ciphertext_length - 32]
    calculated_mac = hmac_sha256(keys[32:], iv, attachment_cipher)
    if mac != calculated_mac:
        raise Exception("bad mac")
    if len(thier_digest) != 16:
        raise Exception("unknown digest")
    calculated_digest = hashlib.md5(ciphertext).digest()
    if calculated_digest != thier_digest:
        raise Exception("digest not match")

    cipher = AES.new(keys[:32], AES.MODE_CBC, iv)
    attachment_cipher = cipher.decrypt(attachment_cipher)
    return pkcs5_unpad(attachment_cipher)
