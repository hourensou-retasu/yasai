import requests
url = "https://accounts.secure.freee.co.jp/public_api/token"
payload = {
  "grant_type": "authorization_code",
  "client_id": "6e4d11db5993f17638e620aae1f25a38c5c95dcdb0c825d1432994ab1d2b0fc0",
  "client_secret": "ce92bc7db869a5e00f00305c3ff7a4c3cda19d15d3f425c6619f04b9b1547b92",
  "code": "6f69ab22a34c619796e94cf0feb14d951eb59460a3b3f6ed7fef4b6d1acb3857",
  "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
}

r = requests.post(url, json=payload)

print(r.text)