from viking.core import Plugin
import cPickle as pickle
from itsdangerous import Signer
import hashlib
import os
import base64
import json
from cryptography.fernet import Fernet

class Serializer(Plugin):
    plugin_namespace = 'serializers'
    abstract_plugin = True

    def __init__(self, signing_key=None, encryption_key=None):
        self.signing_key = signing_key
        self.encryption_key = encryption_key

    @classmethod
    def generate_encryption_key(cls):
        return Fernet.generate_key()

    def serialize(self, obj):
        raise NotImplementedError

    def deserialize(self, data):
        raise NotImplementedError

    def encrypt(self, data):
        return Fernet(self.encryption_key).encrypt(data)

    def decrypt(self, data):
        return Fernet(self.encryption_key).decrypt(data)

    def to_wire(self, obj):
        data = self.serialize(obj)

        if self.encryption_key:
            data = self.encrypt(data)
        if self.signing_key:
            data = Signer(self.signing_key).sign(data)

        return data

    def from_wire(self, data):
        if self.signing_key:
            data = Signer(self.signing_key).unsign(data)

        if self.encryption_key:
            data = self.decrypt(data)

        return self.deserialize(data)

class PickleSerializer(Serializer):
    plugin_name = 'pickle'

    def serialize(self, obj):
        return pickle.dumps(obj)

    def deserialize(self, data):
        return pickle.loads(data)
