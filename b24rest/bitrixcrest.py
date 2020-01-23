from flask import request
import json
import requests
from . import settings

class BitrixCrest:
    BATCH_COUNT = 50  # count   batch    1    query
    TYPE_TRANSPORT = 'json'  # json or xml

    def __init__(self):
        self.C_REST_WEB_HOOK_URL = settings.C_REST_WEB_HOOK_URL
        self.C_REST_CLIENT_ID = settings.C_REST_CLIENT_ID
        self.C_REST_CLIENT_SECRET = settings.C_REST_CLIENT_SECRET

    def install_app(self):
        result = {'rest_only': True, 'install': False}
        auth = {}
        if request.form.get('auth[access_token]'):
            auth['access_token'] = request.form.get('auth[access_token]')
            auth['application_token'] = request.form.get('auth[application_token]')
            auth['client_endpoint'] = request.form.get('auth[client_endpoint]')
            auth['domain'] = request.form.get('auth[domain]')
            auth['expires'] = request.form.get('auth[expires]')
            auth['expires_in'] = request.form.get('auth[expires_in]')
            auth['member_id'] = request.form.get('auth[member_id]')
            auth['refresh_token'] = request.form.get('auth[refresh_token]')
            auth['scope'] = request.form.get('auth[scope]')
            auth['server_endpoint'] = request.form.get('auth[server_endpoint]')
            auth['status'] = request.form.get('auth[status]')
            auth['user_id'] = request.form.get('auth[user_id]')

        if request.form.get('event') == 'ONAPPINSTALL' and bool(auth):
            result['install'] = self.set_app_settings(auth, True)
        elif request.form.get('PLACEMENT') == 'DEFAULT':
            result['rest_only'] = False

            result['install'] = self.set_app_settings({
                'access_token': request.form.get('AUTH_ID'),
                'expires_in': request.form.get('AUTH_EXPIRES'),
                'application_token': request.args.get('APP_SID'),
                'refresh_token': request.form.get('REFRESH_ID'),
                'domain': request.args.get('DOMAIN'),
                'client_endpoint': 'https://' + request.args.get('DOMAIN') + '/rest/',
            }, True)

        # log

        return result

    def set_app_settings(self, settings, isInstall=False):
        result = False
        olddata = self.get_app_settings()

        if isInstall == False and olddata and isinstance(olddata, dict):
            new_settings = olddata.copy()
            new_settings.update(settings)
            settings = new_settings

        result = self.set_setting_data(settings)

        return result

    def get_app_settings(self):
        data = {}
        iscurrdata = False
        if self.C_REST_WEB_HOOK_URL:
            data = {'client_endpoint': self.C_REST_WEB_HOOK_URL, 'is_web_hook': 'Y'}
            iscurrdata = True
        else:
            data = self.get_setting_data()
            iscurrdata = False
            if data.get('access_token') and data.get('domain') and data.get('refresh_token') and data.get(
                    'application_token') and data.get('client_endpoint'):
                iscurrdata = True

        if iscurrdata:
            return data
        else:
            return False

    def set_setting_data(self, settings):
        with open('settings.json', 'w') as settingFile:
            json.dump(settings, settingFile)

        return True

    def get_setting_data(self):
        result = {}
        try:
            with open('settings.json') as settingFile:
                result = json.load(settingFile)
                if result == None:
                    return {}

                if self.C_REST_CLIENT_ID:
                    result['C_REST_CLIENT_ID'] = self.C_REST_CLIENT_ID

                if self.C_REST_CLIENT_SECRET:
                    result['C_REST_CLIENT_SECRET'] = self.C_REST_CLIENT_SECRET
        except IOError:
            print('File not found')

        return result

    def call(self, method, params=None, this_auth=False):
        settings = self.get_app_settings()
        if settings:
            query = {}

            if this_auth:
                url = 'https://oauth.bitrix.info/oauth/token/'
            else:
                url = settings.get('client_endpoint') + method + '.' + self.TYPE_TRANSPORT
                if not settings.get('is_web_hook') or settings.get('is_web_hook') != 'Y':
                    query['auth'] = settings.get('access_token')

            if this_auth:
                query = params
                params = {}

            try:
                r = requests.post(url, json=params, params=query)
            except requests.exceptions.HTTPError as error:
                r = None

            if r.status_code == 200:
                return json.loads(r.text)
            elif r.status_code == 401:
                error = json.loads(r.text)

                if error.get('error') == 'expired_token' and not this_auth:
                   print('GET NEW')
                   return self.get_new_auth(method, params)

                return error
            elif r.status_code == 400:
                return json.loads(r.text)
            else:
                return {'error': 'exception',
                        'error_information': ''}

        return {'error': 'no_install_app',
                'error_information': 'error install app, pls install local application '}

    def get_new_auth(self, method, params):
        result = {}
        settings = self.get_app_settings()

        if settings:
            # authParams = {
            #     'this_auth': 'Y',
            #     'params': {
            #         'client_id': settings['C_REST_CLIENT_ID'],
            #         'grant_type': 'refresh_token',
            #         'client_secret': settings['C_REST_CLIENT_SECRET'],
            #         'refresh_token': settings['refresh_token']
            #     }
            # }
            authParams = {
                'client_id': settings['C_REST_CLIENT_ID'],
                'grant_type': 'refresh_token',
                'client_secret': settings['C_REST_CLIENT_SECRET'],
                'refresh_token': settings['refresh_token']
            }

            data = self.call('', authParams, this_auth=True)

            if self.set_app_settings(data):
               result = self.call(method, params)

        return result
