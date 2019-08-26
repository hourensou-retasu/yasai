import requests
import datetime

from refreshToken import refreshToken

class freeeAPI:
  def __init__(self):

    with open("./freeeAPIAccessToken") as f:
      accessToken = f.read()

    self.headers = {
      "Authorization": f'Bearer { accessToken }'
    }

    self.APIbaseURL = "https://api.freee.co.jp/hr/api/v1"

    url = self.APIbaseURL + "/users/me"
    res = requests.get(url, headers=self.headers)

    if res.status_code == 401:
      refreshToken()
      res = requests.get(url, headers=self.headers)

    self.companyID = res.json()["companies"][0]["id"]

  def __doGET(self, url):
    res = requests.get(url, headers=self.headers)
    if res.status_code == 401:
      refreshToken()
      res = requests.get(url, headers=self.headers)
    return res.json()

  def __doPOST(self, url, data):
    res = requests.post(url, headers=self.headers, json=data)
    if res.status_code == 401:
      refreshToken()
      res = requests.get(url, headers=self.headers)
    return res.json()

  def __timeClocks(self, employeeID, clockType):
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    url = self.APIbaseURL + f"/employees/{ employeeID }/time_clocks"
    data = {
      "company_id": self.companyID,
      "type": clockType,
      "base_date": date
    }

    res = self.__doPOST(url, data)
    return res


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
    return self.__timeClocks(employeeID, "clock_in")

  def clockOut(self, employeeID):
    return self.__timeClocks(employeeID, "clock_out")

  def breakBegin(self, employeeID):
    return self.__timeClocks(employeeID, "break_begin")

  def breakEnd(self, employeeID):
    return self.__timeClocks(employeeID, "break_end")


if __name__ == "__main__":
  freee = freeeAPI()

  print(freee.getCompanyID())