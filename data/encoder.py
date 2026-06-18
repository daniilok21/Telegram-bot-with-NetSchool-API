from dotenv import load_dotenv
load_dotenv()
import os
from cryptography.fernet import Fernet

cipher = Fernet(os.getenv("ENCRYPTION_KEY").encode())
#шифровать
def encrypt(value: str) -> str:  
    return cipher.encrypt(value.encode()).decode()
#расшифровать
def decrypt(value: str) -> str:
    return cipher.decrypt(value.encode()).decode()