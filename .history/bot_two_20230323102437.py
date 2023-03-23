import requests

url = "http://127.0.0.1:5000/get-order-book"

payload = "\"wrkn\""
headers = {
  'Content-Type': 'text/plain'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
