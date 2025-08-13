import getpass
import json
import os
from pathlib import Path
import re
import threading
import time
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse, parse_qs, unquote

from walker.config import Config
from walker.k8s_utils.custom_resources import CustomResources
from walker.k8s_utils.ingresses import Ingresses
from walker.k8s_utils.kube_context import KubeContext
from walker.utils import json_to_csv, lines_to_tabular, log, log2
from walker.apps import Apps

class AppSession:
    sessions_by_sts = {}
    sessions_by_host = {}

    def __init__(self, host: str = None, env: str = None):
        self.host = host
        self.env = env
        self.session: requests.Session = None

    def create_for_sts(sts: str, namespace: str) -> 'AppSession':
        key = f'{sts}@{namespace}'
        if key in AppSession.sessions_by_sts:
            return AppSession.sessions_by_sts[key]

        app_id = CustomResources.get_app_id(sts, namespace)
        if not app_id:
            log2('Cannot locate app custom resource.')

            return None

        h3 = app_id.split('-')
        ingress_name = Config().get('app.login.ingress', '{app_id}-k8singr-appleader-001').replace('{app_id}', app_id)
        host = f"{Ingresses.get_host(ingress_name, namespace)}/{h3[1]}/{h3[2]}"
        if not host:
            log2('Cannot locate ingress for app.')

            return None

        session = AppSession(host)

        AppSession.sessions_by_sts[key] = session

        return session

    def create(env: str, app: str, namespace: str = None) -> 'AppSession':
        if not namespace:
            namespace = Apps.find_namespace(env)

        ingress_name = Config().get('app.login.ingress', '{app_id}-k8singr-appleader-001').replace('{app_id}', f'{namespace}-{env}-{app}')
        host = Ingresses.get_host(ingress_name, namespace)
        if not host:
            log2('Cannot locate ingress for app.')

            return None

        key = f'{host}/{env}'
        if key in AppSession.sessions_by_host:
            return AppSession.sessions_by_host[key]

        session = AppSession(host, env)

        AppSession.sessions_by_host[key] = session

        return session

    def run(env: str, app: str, namespace: str, type: str, action: str, payload: any = None, forced = False):
        app_session: AppSession = AppSession.create(env, app, namespace)
        session = app_session.login(forced=forced)
        if session:
            with session as session:
                uri = f'https://{app_session.host}/{env}/{app}/api/8/{type}/{action}'
                r = session.post(uri, json=payload, headers={
                    'X-Request-Envelope': 'true'
                })

                if Config().get('debug.show-out', False):
                    log2(f'{r.status_code} {uri}')
                    log2(payload)

                if r.status_code >= 200 and r.status_code < 300 or r.status_code == 400:
                    try:
                        js = r.json()
                        try:
                            header, lines = json_to_csv(js, delimiter='\t')
                            log(lines_to_tabular(lines, header=header, separator='\t'))
                        except:
                            log(js)
                    except:
                        if r.text:
                            log2('Failed parsing the results.')
                else:
                    log2(r.status_code)
                    log2(r.text)

    def login(self, forced = False) -> requests.Session:
        if not forced and self.session:
            return self.session

        if not(idp_uri := self.redirect_uri()):
            return None

        idp_url = urlparse(idp_uri)
        idp = idp_url.hostname
        if not 'OKTA' in idp.upper():
            log2(f'{idp} is not supported; only okta.com is supported.')

            return None

        okta = idp.upper().split('.')[0]
        env_f = f'{Path.home()}/.kaqing/.credentials'
        load_dotenv(dotenv_path=env_f)

        username = None
        while not username:
            default_user = os.getenv(f'{okta}_USERNAME')
            if default_user:
                if forced:
                    username = default_user
                else:
                    username = input(f'Username(default {default_user}): ') or default_user
            else:
                username = input(f'Username: ')
        password = None
        while not password:
            default_pass = os.getenv(f'{okta}_PASSWORD')
            if default_pass:
                if forced:
                    password = default_pass
                else:
                    password = getpass.getpass(f'Password(default ********): ') or default_pass
            else:
                password = getpass.getpass(f'Password: ')

        session = self.okta_login(idp_uri, username, password)
        if session:
            self.session = session

            if Config().get('app.login.cache-creds', True):
                updated = []
                if os.path.exists(env_f):
                    with open(env_f, 'r') as file:
                        try:
                            file_content = file.read()
                            for l in file_content.split('\n'):
                                tks = l.split('=')
                                key = tks[0]
                                value = tks[1] if len(tks) > 1 else ''
                                if key == f'{okta}_USERNAME':
                                    value = username
                                elif key == f'{okta}_PASSWORD' and not KubeContext.in_cluster():
                                    # do not store password to the .credentials file when in Kubernetes pod
                                    value = password
                                updated.append(f'{key}={value}')
                        except:
                            updated = None
                            log2('Update failed')
                else:
                    updated.append(f'{okta}_USERNAME={username}')
                    if not KubeContext.in_cluster():
                        # do not store password to the .credentials file when in Kubernetes pod
                        updated.append(f'{okta}_PASSWORD={password}')

                if updated:
                    with open(env_f, "w") as file:
                        file.write('\n'.join(updated))

        return session

    def redirect_uri(self) -> str:
        # stgawsscpsr-c3-c3
        uri = Config().get('app.login.url', 'https://{host}/{env}/{app}/static/console/index.html').replace('{host}', self.host).replace('{env}', self.env).replace('{app}', 'c3')
        r = requests.get(uri)

        parsed_url = urlparse(r.url)
        log2(f'{r.status_code} {uri} <-> {parsed_url.hostname}...')
        if r.status_code < 200 or r.status_code > 299:
            return None

        return r.url

    def okta_login(self, idp_uri: str, username: str, password: str) -> requests.Session:
        parsed_url = urlparse(idp_uri)
        query_string = parsed_url.query
        params = parse_qs(query_string)
        state_token = params.get('state', [''])[0]
        redirect_url = params.get('redirect_uri', [''])[0]

        okta_host = parsed_url.hostname

        url = f"https://{okta_host}/api/v1/authn"
        payload = {
            "username": username,
            "password": password,
            "options": {
                "warnBeforePasswordExpired": True,
                "multiOptionalFactorEnroll": False
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        session = requests.Session()
        response = session.post(url, headers=headers, data=json.dumps(payload))
        if Config().get('debug.show-out', False):
            log2(f'{response.status_code} {url}')
        auth_response = response.json()

        if 'sessionToken' not in auth_response:
            return None

        session_token = auth_response['sessionToken']

        url = f'{idp_uri}&sessionToken={session_token}'
        r = session.get(url)
        if Config().get('debug.show-out', False):
            log2(f'{r.status_code} {url}')

        id_token = AppSession.extract(r.text, r'.*name=\"id_token\" value=\"(.*?)\".*')
        if not id_token:
            err = AppSession.extract(r.text, r'.*name=\"error_description\" value=\"(.*?)\".*')
            if err:
                log2(unquote(err).replace('&#x20;', ' '))
            else:
                log2('id_token not found\n' + r.text)

            return None

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        form_data = {
            'state': state_token,
            'id_token': id_token
        }

        stop_event = threading.Event()

        def login():
            try:
                timeout = Config().get('app.login.timeout', 5)
                if Config().get('debug.show-out', False):
                    log2(f'-> {redirect_url}')
                session.post(redirect_url, headers=headers, data=form_data, timeout=timeout)
            except Exception:
                pass
            finally:
                stop_event.set()

        my_thread = threading.Thread(target=login, daemon=True)
        my_thread.start()

        access_token = None
        while not access_token and not stop_event.is_set():
            time.sleep(1)

            try:
                check_uri = Config().get('app.login.session-check-url', 'https://{host}/{env}/{app}/api/8/C3/userSessionToken').replace('{host}', self.host).replace('{env}', self.env).replace('{app}', 'c3')
                r = session.get(check_uri)
                if Config().get('debug.show-out', False):
                    log2(f'{r.status_code} {check_uri}')

                access_token = r.json()['signedToken']
            except Exception:
                pass

        return session

    def extract(form: str, pattern: re.Pattern):
        value = None

        for l in form.split('\n'):
            # <input type="hidden" name="id_token" value="..."/>
            groups = re.match(pattern, l)
            if groups:
                value = groups[1]

        return value