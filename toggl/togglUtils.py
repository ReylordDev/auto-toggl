def handleRequestErrors(response):
    print(response.status_code)
    print(response.json())
    raise Exception("TogglRequest failed")
