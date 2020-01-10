import json

C_REST_CLIENT_ID = ''
C_REST_CLIENT_SECRET = ''
C_REST_WEB_HOOK_URL = ''

def savedata(settings):
    with open('settings.json', 'w') as settingFile:
        json.dump(settings, settingFile)

    return True

def getdata():
    with open('settings.json') as settingFile:
        result = json.load(settingFile)
        return result

    return {}