import requests
import json

url = "https://accounts.secure.freee.co.jp/public_api/token"



with open("freeeAPIsecret.json") as f:
  payload = json.load(f)

print("認可コードを入力してください：")
authCode = input().strip()
payload["code"] = authCode

r = requests.post(url, json=payload)
print(r.text)

if r.status_code != 401:
  with open("freeeAPIAccessToken", "w") as f:
    f.write(r.json()["access_token"])
  
  with open("freeeAPIRefreshToken", "w") as f:
    f.write(r.json()["refresh_token"])
