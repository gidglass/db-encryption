from __future__ import absolute_import, division, print_function

import base64
import binascii
import os
import struct
import time
import six
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class InvalidToken(Exception):
    pass

class Fernet2(object):
  def __init__(self, key, backend=None):
    if backend is None:
      backend = default_backend()

    key = base64.urlsafe_b64decode(key)
    if len(key) != 32:
      raise ValueError(
        "Fernet key must be 32 url-safe base64-encoded bytes."
    )

    h = HMAC(key, hashes.SHA256(), backend=backend)
    h.update(b"\x00")
    self._signing_key = h.finalize()[:16]

    h = HMAC(key, hashes.SHA256(), backend=backend)
    h.update(b"\x01")
    self._encryption_key = h.finalize()[:16]

    self._backend = backend

  @classmethod
  def generate_key(cls):
    return base64.urlsafe_b64encode(os.urandom(32))

  def encrypt(self, data, associated_data=b""):
    iv = os.urandom(16)
    return self._encrypt_from_parts(data, iv, associated_data)

  def _encrypt_from_parts(self, data, iv, associated_data):
    if not isinstance(data, bytes):
      raise TypeError("data must be bytes.")

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    encryptor = Cipher(
        algorithms.AES(self._encryption_key), modes.CBC(iv), self._backend
    ).encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    basic_parts = (
      b"\x81" + iv + ciphertext + associated_data
    )

    h = HMAC(self._signing_key, hashes.SHA256(), backend=self._backend)
    h.update(basic_parts)
    hmac = h.finalize() # TAG

    return base64.urlsafe_b64encode(b"\x81" + iv + ciphertext + hmac)

  def decrypt(self, token, associated_data=b"", ttl=None):
    if not isinstance(token, bytes):
      raise TypeError("token must be bytes.")

    current_time = int(time.time())

    try:
      data = base64.urlsafe_b64decode(token)
    except (TypeError, binascii.Error):
      raise InvalidToken

    if not data or (six.indexbytes(data, 0) != 0x81):
      raise InvalidToken

    h = HMAC(self._signing_key, hashes.SHA256(), backend=self._backend)
    h.update(data[:-32] + associated_data)
    try:
      h.verify(data[-32:])
    except InvalidSignature:
      raise InvalidToken
    iv = data[1:17]
    ciphertext = data[17:-32]

    decryptor = Cipher(
      algorithms.AES(self._encryption_key), modes.CBC(iv), self._backend
    ).decryptor()

    plaintext_padded = decryptor.update(ciphertext)
    try:
      plaintext_padded += decryptor.finalize()
    except ValueError:
      raise InvalidToken
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

    unpadded = unpadder.update(plaintext_padded)
    try:
      unpadded += unpadder.finalize()
    except ValueError:
      raise InvalidToken
    return unpadded

# class PwFernet(object):
#     def __init__(self, password, backend=None):
#         if backend is None:
#             backend = default_backend()
#         self._password = password
#         self._backend = backend

#     @classmethod
#     def generate_password(cls):
#         return base64.urlsafe_b64encode(os.urandom(32))

#     def _generate_keys(self, salt=None):
#         if salt == None:
#             salt = os.urandom(16)
#         kdf = PBKDF2HMAC(
#             algorithm = hashes.SHA256(),
#             length = 32,
#             salt = salt,
#             iterations = 100000,
#             backend = self._backend
#         )
#         key = base64.urlsafe_b64encode(kdf.derive(self._password))
#         self._signing_key = key[16:]
#         self._encryption_key = key[:16]
#         self._salt = salt

#     def encrypt(self, data, associated_data=b""):
#         self._generate_keys() # Generate fresh salt with each encryption
#         return self._encrypt_from_parts(data, self._salt, associated_data)

#     def _encrypt_from_parts(self, data, salt, associated_data):
#         if not isinstance(data, bytes):
#             raise TypeError("data must be bytes.")

#         padder = padding.PKCS7(algorithms.AES.block_size).padder()
#         padded_data = padder.update(data) + padder.finalize()
#         encryptor = Cipher(
#             algorithms.AES(self._encryption_key), modes.CBC(salt), self._backend
#         ).encryptor()
#         ciphertext = encryptor.update(padded_data) + encryptor.finalize()

#         basic_parts = (
#             b"\x82" + salt + ciphertext + associated_data
#         )

#         h = HMAC(self._signing_key, hashes.SHA256(), backend=self._backend)
#         h.update(basic_parts)
#         hmac = h.finalize() # TAG

#         return base64.urlsafe_b64encode(b"\x82" + salt + ciphertext + hmac)

#     def decrypt(self, token, associated_data=b"", ttl=None):
#         if not isinstance(token, bytes):
#             raise TypeError("token must be bytes.")

#         current_time = int(time.time())

#         try:
#             data = base64.urlsafe_b64decode(token)
#         except (TypeError, binascii.Error):
#             raise InvalidToken

#         if not data or (six.indexbytes(data, 0) != 0x82):
#             raise InvalidToken

#         salt = data[1:17]
#         ciphertext = data[17:-32]

#         self._generate_keys(salt) # Generate matching keys from token salt

#         h = HMAC(self._signing_key, hashes.SHA256(), backend=self._backend)
#         h.update(data[:-32] + associated_data)
        
#         try:
#             h.verify(data[-32:])
#         except InvalidSignature:
#             raise InvalidToken
        
#         decryptor = Cipher(
#             algorithms.AES(self._encryption_key), modes.CBC(salt), self._backend
#         ).decryptor()
#         plaintext_padded = decryptor.update(ciphertext)
#         try:
#             plaintext_padded += decryptor.finalize()
#         except ValueError:
#             raise InvalidToken
#         unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

#         unpadded = unpadder.update(plaintext_padded)
#         try:
#             unpadded += unpadder.finalize()
#         except ValueError:
#             raise InvalidToken
#         return unpadded

# class MultiFernet(object):
#     def __init__(self, fernets):
#         fernets = list(fernets)
#         if not fernets:
#             raise ValueError(
#                 "MultiFernet requires at least one Fernet instance"
#             )
#         self._fernets = fernets

#     def encrypt(self, msg):
#         return self._fernets[0].encrypt(msg)

#     def decrypt(self, msg, ttl=None):
#         for f in self._fernets:
#             try:
#                 return f.decrypt(msg, ttl)
#             except InvalidToken:
#                 pass
#         raise InvalidToken
