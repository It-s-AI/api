import requests

url = "http://0.0.0.0:13337/detect/"

headers = {
    'Content-Type': 'application/json',
    'auth': 'auth_key'
}

body = {
    "text": ["sample text 1", "sample text 2"],
    "N_AXONS": 10,
    "SORT_TYPE": "uid",
    "TIMEOUT": 3,
    "ORDERING": "desc"
}

response = requests.post(url, json=body, headers=headers)

print(f"Status Code: {response.status_code}")
from pprint import pprint
print(f"Response Body")
pprint(response.json())