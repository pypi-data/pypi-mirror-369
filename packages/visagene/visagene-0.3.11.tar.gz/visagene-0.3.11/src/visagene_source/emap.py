import hashlib
import io
import os

import cupy as cp
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))


def load_emap(emap_path: str | None = None) -> cp.ndarray:
    if emap_path is None:
        emap_path = os.path.join(script_dir, "emap.bin")
    if not os.path.exists(emap_path):
        raise FileNotFoundError(f"EMAP file not found: {emap_path}")

    password = "visagene"
    key = hashlib.sha256(password.encode()).digest()

    with open(emap_path, "rb") as f:
        encrypted_data = f.read()

    decrypted = bytearray()
    for i in range(len(encrypted_data)):
        decrypted.append(encrypted_data[i] ^ key[i % len(key)])

    buffer = io.BytesIO(decrypted)

    return cp.asarray(np.load(buffer))


def save(array: np.ndarray, dest_path: str | None = None):
    password = "visagene"
    key = hashlib.sha256(password.encode()).digest()

    buffer = io.BytesIO()
    np.save(buffer, array)
    encrypted = bytearray()
    for i in range(len(buffer.getvalue())):
        encrypted.append(buffer.getvalue()[i] ^ key[i % len(key)])

    if dest_path is None:
        dest_path = os.path.join(script_dir, "emap.bin")
    with open(dest_path, "wb") as f:
        f.write(encrypted)


if __name__ == "__main__":
    # Example usage
    emap = load_emap()
    # print("EMAP loaded successfully.")
    # print(f"EMAP shape: {emap.shape}")

    # Save the EMAP back (for testing purposes)
    save(emap)
    # print("EMAP saved successfully.")
