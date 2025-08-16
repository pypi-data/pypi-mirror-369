# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
test_3 = os.getenv("test3")
brevo_api_key = os.getenv("testing")
print(brevo_api_key)

print(SUPABASE_URL)
print(SUPABASE_KEY)
print(test_3)

def verify_js_password(password: str, stored_hash: str) -> bool:
    try:
        # Print debug information
        print(f"Attempting to verify password")
        print(f"Hash length: {len(stored_hash)}")

        # Decode the stored hash
        combined = base64.b64decode(stored_hash.encode('utf-8'))
        print(f"Decoded combined length: {len(combined)} bytes")

        salt = combined[:16]
        stored_hash_bytes = combined[16:]

        print(f"Salt length: {len(salt)} bytes")
        print(f"Stored hash length: {len(stored_hash_bytes)} bytes")

        # Create PBKDF2 instance
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        # Derive the key
        derived_hash = kdf.derive(password.encode('utf-8'))
        print(f"Derived hash length: {len(derived_hash)} bytes")

        # Compare the hashes
        result = bytes(stored_hash_bytes) == bytes(derived_hash)
        print(f"Hash comparison result: {result}")

        # Also show the actual bytes for debugging
        print(f"Stored hash bytes: {stored_hash_bytes.hex()}")
        print(f"Derived hash bytes: {derived_hash.hex()}")

        return result
    except Exception as e:
        print(f"Error during verification: {str(e)}")
        return False

# Test the verification
password = "MSNI2691*"
stored_hash = "NqUyhDOC/pGrWF3zhlKNUlTkcKpWu6u8qJhafZlWb8zYpHfqTFaCOf1ejNmT+qwl"

result = verify_js_password(password, stored_hash)
print(f"\nFinal verification result: {result}")
