import requests

url = "http://127.0.0.1:18889/detect/"

headers = {
    'Content-Type': 'application/json',
    'auth': 'auth_key123'
}

body = {
    "text": ["sample text 1", "sample text 2"],
    "N_AXONS": 256,
    "SORT_TYPE": "emission",
    "TIMEOUT": 15,
}

response = requests.post(url, json=body, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.json()}")