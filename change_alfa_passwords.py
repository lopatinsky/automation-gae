from requests import Session

LOGINS = []  # TODO put a list of logins here

DEFAULT_PASSWORD = "Password*1"
NEW_PASSWORD = ""  # TODO put new password here

HOST = "https://engine.paymentgate.ru"
PAGE_URL = HOST + "/mportal/"
LOGIN_URL = HOST + "/mportal/login"
CHANGE_PASSWORD_URL = HOST + "/mportal/mvc/user/changepassword"

default_headers = {
    "Accept-Language": "ru,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.97 "
                  "YaBrowser/15.9.2403.2152 (beta) Safari/537.36"
}
ajax_headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": PAGE_URL,
    "Origin": HOST,
}

for login in LOGINS:
    print login,

    s = Session()
    s.headers.update(default_headers)
    s.get(PAGE_URL)

    login_resp = s.post(LOGIN_URL, {
        "username": login,
        "password": DEFAULT_PASSWORD
    }, headers=ajax_headers)
    if login_resp.status_code != 200:
        print "fail on login", login_resp.text
        continue

    change_resp = s.post(CHANGE_PASSWORD_URL, {
        "password": NEW_PASSWORD,
        "repeatPassword": NEW_PASSWORD
    }, headers=ajax_headers)
    if change_resp.status_code != 200:
        print "fail on change", change_resp.text
        continue

    print "success"
