from datetime import datetime
from RSA import *
import hashlib

class Message:

    def __init__(self, message, sender, receiver, public_key, signing_private_key):
        self.timestamp = datetime.now()
        self.public_key = public_key
        self.signature = self.signing(message, signing_private_key)
        print(message + self.signature)
        self.message = rsa_encryption(message + self.signature, self.public_key)
        print(self.message)
        self.sender = sender
        self.receiver = receiver

    def signing(self, message, signing_private_key):
        if (signing_private_key == ""):
            return ""
        else:
            message_digest = hashlib.sha256(message.encode()).hexdigest()
            signature = rsa_encryption(message_digest, signing_private_key)
            print("String : ", end ="")
            print(message)
            print("Hash Value : ", end ="")
            print(message_digest)
            print("Signature : ", signature)
            return "<ds>" + signature + "</ds>"

    def to_json(self):
        return {
            "timestamp": str(self.timestamp),
            "sender": self.sender,
            "receiver": self.receiver,
            "message": self.message
        }

def verify(message, signature, public_key_verifying):
    if (len(signature) == 0):
        return False
    else:
        message_digest_original = hashlib.sha256(message.encode()).hexdigest()
        message_digest_signature = rsa_decryption(signature, public_key_verifying)
        return (message_digest_original == message_digest_signature)
