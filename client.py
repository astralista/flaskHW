import requests

# response = requests.post('http://127.0.0.1:5000/ads/',
#                          json={'name': 'user_2', 'password': '12gsdedsgsdgesgeg34'})
# print(response.status_code)
# print(response.text)

response = requests.delete(
    "http://127.0.0.1:5000/ads/1",
)

print(response.status_code)
print(response.text)

response = requests.get("http://127.0.0.1:5000/ads/1")

print(response.status_code)
print(response.text)
