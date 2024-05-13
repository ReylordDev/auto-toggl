def handleRequestErrors(response):
    status_code = response.status_code
    print(status_code)
    if status_code == 504:
        print("Gateway Timeout")
        return
    print(response.text)
    raise Exception("TogglRequest failed")
