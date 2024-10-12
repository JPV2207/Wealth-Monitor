from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

static_key = bos.getenv('SUPER_SECRET_KEY')

# Initialize the AES cipher with ECB mode
backend = default_backend()
cipher = Cipher(algorithms.AES(static_key), modes.ECB(), backend=backend)


# Encrypt username
os.getenv('USERNAME')

encryptor = cipher.encryptor()
padded_username = username.ljust(32)  # Pad username to 32 bytes (AES block size)
encrypted_username = encryptor.update(padded_username.encode()) + encryptor.finalize()

# Decrypt username
decryptor = cipher.decryptor()
decrypted_username = decryptor.update(encrypted_username) + decryptor.finalize()
decrypted_username = decrypted_username.decode().rstrip()  # Remove padding and decode to string

#print("Original username:", username)
print("Encrypted username:", encrypted_username)
#print("Decrypted username:", decrypted_username)
