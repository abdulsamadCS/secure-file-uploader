from cryptography.fernet import Fernet


def encrypt_file(file_content):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted_content = fernet.encrypt(file_content)
    return encrypted_content, key.decode()
