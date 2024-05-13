def handleRequestErrors(response):
    print(response.status_code)
    print(response.text)
    raise Exception("TogglRequest failed")
