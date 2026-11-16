"""Double-spend demo against a running server.

    python scripts/race.py http://127.0.0.1:8000
"""
import sys
import threading

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
N = 10

token = requests.post(f"{BASE}/api/auth/login",
                      json={"username": "bob", "password": "bob-pass-1"}).json()["token"]
h = {"Authorization": f"Bearer {token}"}
before = requests.get(f"{BASE}/api/me", headers=h).json()["balance_eur"]
if float(before) == 0:
    sys.exit("bob has 0 EUR, re-seed the database first (see README)")

barrier = threading.Barrier(N)
codes = []


def go():
    barrier.wait()
    r = requests.post(f"{BASE}/api/transfers", headers=h,
                      json={"to": "SI56100000000000001", "amount": before})
    codes.append(r.status_code)


threads = [threading.Thread(target=go) for _ in range(N)]
[t.start() for t in threads]
[t.join() for t in threads]

ok = codes.count(201)
print(f"bob had {before} EUR, sent {N} transfers of {before} EUR at once")
print(f"accepted: {ok}, rejected: {N - ok}")
print("double spend!" if ok > 1 else "no race this time, try again")
