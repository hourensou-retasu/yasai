import requests
import json

def refreshToken():
  url = "https://accounts.secure.freee.co.jp/public_api/token"

  with open("freeeAPIsecret.json") as f:
    payload = json.load(f)

  payload["grant_type"] = "refresh_token"
  
  with open("freeeAPIRefreshToken") as f:
    payload["refresh_token"] = f.read()

  r = requests.post(url, json=payload)
  print(r.text)
  
  if r.status_code == 401:
    return

  with open("freeeAPIAccessToken", "w") as f:
    f.write(r.json()["access_token"])

  with open("freeeAPIRefreshToken", "w") as f:
    f.write(r.json()["refresh_token"])

if __name__ == "__main__":
  refreshToken()