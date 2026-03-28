import hashlib


def hash_password(password: str) -> str:
    """
    Hashes a password using SHA-256.
    SHA-256 is universally supported across almost all programming languages
    (Java, C#, JavaScript/Node.js, PHP, Go, etc.) without needing external libraries.
    """

    password_bytes = password.encode("utf-8")

    hash_object = hashlib.sha256(password_bytes)

    return hash_object.hexdigest()
