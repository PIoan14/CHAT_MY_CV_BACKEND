import hashlib

def hash_password(password: str) -> str:
    """
    Hashes a password using SHA-256.
    SHA-256 is universally supported across almost all programming languages
    (Java, C#, JavaScript/Node.js, PHP, Go, etc.) without needing external libraries.
    """
    # 1. Convert the string to bytes
    password_bytes = password.encode('utf-8')
    
    # 2. Create a SHA-256 hash object
    hash_object = hashlib.sha256(password_bytes)
    
    # 3. Get the hexadecimal representation of the hash
    return hash_object.hexdigest()



# my_password = "parola_mea_super_secreta"
# hashed = hash_password(my_password)
    
# print("-" * 50)
# print(f"Original Password : {my_password}")
# print(f"SHA-256 Hash : {hashed}")
# print("-" * 50)