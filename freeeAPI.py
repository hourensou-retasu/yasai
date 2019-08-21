import requests
import datetime

class freeeAPI:
  def __init__(self):
    self.token = {
      "access_token": "fa1c9c5b54fa02ec15d41b980781b1b49a7b92aa32bf05302706f5b095c90294",
      "token_type": "bearer",
      "expires_in": 86400,
      "refresh_token": "47b7741f8f642c25a8241a577b642d88cd6d22b16993e25b99a7d3ed8f065f5b",
      "scope": "read write default_read",
      "created_at": 1566349456
    }

    self.headers = {
      "Authorization": f'Bearer { self.token["access_token"] }'
    }

    self.APIbaseURL = "https://api.freee.co.jp/hr/api/v1"

    url = self.APIbaseURL + "/users/me"
    res = requests.get(url, headers=self.headers)

    self.companyID = res.json()["companies"][0]["id"]

  def __doGET(self, url):
    res = requests.get(url, headers=self.headers)
    return res.json()

  def __doPOST(self, url, data):
    res = requests.post(url, headers=self.headers, json=data)
    return res.json()
  

  def getCompanyID(self):
    return self.companyID

  def getEmployeeID(self):
    url = self.APIbaseURL + "/users/me"
    return self.__doGET(url)["companies"][0]["employee_id"]
  
  def getEmployees(self):
    url = self.APIbaseURL + f"/companies/{ self.companyID }/employees"
    res = self.__doGET(url)
    return res

  def clockIn(self, employeeID):
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    url = self.APIbaseURL + f"/employees/{ employeeID }/time_clocks"
    data = {
      "company_id": self.companyID,
      "type": "clock_in",
      "base_date": date
    }

    res = self.__doPOST(url, data)
    return res

  def clockOut(self, employeeID):
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    url = self.APIbaseURL + f"/employees/{ employeeID }/time_clocks"
    data = {
      "company_id": self.companyID,
      "type": "clock_out",
      "base_date": date
    }

    res = self.__doPOST(url, data)
    return res


if __name__ == "__main__":
  freee = freeeAPI()

  print(freee.clockOut(611161))