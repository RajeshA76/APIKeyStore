from cryptography.fernet import Fernet



def generate_encryption_key() -> str:
    key = Fernet.generate_key()
    return key.decode()


def encrypt(key,plain_message)-> bytes:
    message_bytes = plain_message.encode()
    F_key = Fernet(key)
    return F_key.encrypt(message_bytes)


def decrypt(encrypted_message,key)-> str:
    F_key = Fernet(key)
    message_bytes = F_key.decrypt(encrypted_message)
    return message_bytes.decode()