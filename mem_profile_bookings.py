from memory_profiler import profile
import requests
import json

BASE_URL = "http://localhost:5002"

headers = {
    "X-Role": "regular_user",
    "X-User-Id": "5",
    "Content-Type": "application/json",
}

@profile
def mem_test():
    """
    Call POST /bookings multiple times to observe memory usage
    of the Bookings service client process.
    """
    for i in range(10):
        body = {
            "user_id": 5,
            "room_id": 1,
            "start_time": f"2025-11-26T10:{i:02d}:00",
            "end_time":   f"2025-11-26T11:{i:02d}:00",
        }
        r = requests.post(f"{BASE_URL}/bookings",
                          headers=headers,
                          data=json.dumps(body))
        print(i, r.status_code)

if __name__ == "__main__":
    mem_test()
