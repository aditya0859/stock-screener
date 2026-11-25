import os
import requests
from dotenv import load_dotenv

load_dotenv()

r = requests.get(
    "https://api.dhan.co/v2/profile",
    headers={"access-token": os.getenv("DHAN_ACCESS_TOKEN")},
    timeout=10,
)
print("Status:", r.status_code)
print(r.text)