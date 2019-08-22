import requests
import json

def refreshToken():
  url = "https://accounts.secure.freee.co.jp/public_api/token"

  with open("freeeAPIRefreshToken.json") as f:
    payload = json.load(f)

  r = requests.post(url, json=payload)
  print(r.text)

  with open("freeeAPIAccessToken", "w") as f:
    f.write(r["access_token"])