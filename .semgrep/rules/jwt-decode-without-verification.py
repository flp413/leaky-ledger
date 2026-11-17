import jwt

# ruleid: jwt-decode-without-verification
jwt.decode(token, options={"verify_signature": False})

# ruleid: jwt-decode-without-verification
jwt.decode(token, key, verify=False)

# ok: jwt-decode-without-verification
jwt.decode(token, key, algorithms=["HS256"])
