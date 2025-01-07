from pwdlib import PasswordHash

context = PasswordHash.recommended()

def password_to_hash(password: str):
    return context.hash(password)

def hash_to_password(clear_password:str, hashed_password:str):
    return context.verify(clear_password, hashed_password)