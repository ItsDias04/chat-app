from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import os


def encrypt_text(key, text):
    key = key.ljust(32, ' ')  # При необходимости, дополните ключ пробелами до 32 байт
    key = key.encode('utf-8')

    text = text.encode('utf-8')

    # Генерация случайного вектора инициализации
    iv = os.urandom(16)

    # Используем режим CBC с PKCS7 Padding
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Добавляем IV к зашифрованным данным для использования при расшифровании
    encrypted_text = encryptor.update(text) + encryptor.finalize()
    encrypted_text = base64.b64encode(iv + encrypted_text).decode('utf-8')

    return encrypted_text


def decrypt_text(key, encrypted_text):
    key = key.ljust(32, ' ')
    key = key.encode('utf-8')

    encrypted_text = base64.b64decode(encrypted_text.encode('utf-8'))

    # Извлекаем IV из зашифрованных данных
    iv = encrypted_text[:16]
    ciphertext = encrypted_text[16:]

    # Используем режим CBC с PKCS7 Padding
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Расшифровываем данные
    decrypted_text = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypted_text.decode('utf-8')


# Пример использования
# key = "your_secret_key"
# text_to_encrypt = "Hello, AES!"
# encrypted_text = encrypt_text(key, text_to_encrypt)
# print(f'Encrypted Text: {encrypted_text}')
#
# decrypted_text = decrypt_text(key, encrypted_text)
# print(f'Decrypted Text: {decrypted_text}')