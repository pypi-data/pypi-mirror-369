import getpass
import json
import os
from pathlib import Path
import re
import threading
import time
from dotenv import load_dotenv
import jwt
import jwt.algorithms
import requests
from urllib.parse import urlparse, parse_qs, unquote

from walker.config import Config
from walker.k8s_utils.custom_resources import CustomResources
from walker.k8s_utils.ingresses import Ingresses
from walker.k8s_utils.kube_context import KubeContext
from walker.utils import json_to_csv, lines_to_tabular, log, log2
from walker.apps import Apps

class AppSession:
    ctrl_c_entered = False

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
        session, _ = app_session.login(forced=forced)
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
                            log2(r.text)
                else:
                    log2(r.status_code)
                    log2(r.text)

    def login(self, forced = False, use_access_token = True) -> tuple[requests.Session, str]:
        if not forced and self.session:
            return self.session, None

        if not(idp_uri := self.redirect_uri()):
            return None, None

        idp_url = urlparse(idp_uri)
        idp = idp_url.hostname
        if not 'OKTA' in idp.upper():
            log2(f'{idp} is not supported; only okta.com is supported.')

            return None, None

        okta = idp.upper().split('.')[0]
        dir = f'{Path.home()}/.kaqing'
        env_f = f'{dir}/.credentials'
        load_dotenv(dotenv_path=env_f)

        if use_access_token:
            if access_token := os.getenv('ACCESS_TOKEN'):
                session = requests.Session()
                session.cookies.set("c3auth", access_token, domain=self.host, path="/")

                return session, access_token

        # c3energy.okta.com login:
        # Password:
        username = None
        while not username or AppSession.ctrl_c_entered:
            if AppSession.ctrl_c_entered:
                AppSession.ctrl_c_entered = False

            default_user = os.getenv(f'{okta}_USERNAME')
            if default_user:
                if forced:
                    username = default_user
                else:
                    username = input(f'{idp} login(default {default_user}): ') or default_user
            else:
                username = input(f'{idp} login: ')
        password = None
        while not password or AppSession.ctrl_c_entered:
            if AppSession.ctrl_c_entered:
                AppSession.ctrl_c_entered = False

            default_pass = os.getenv(f'{okta}_PASSWORD')
            if default_pass:
                if forced:
                    password = default_pass
                else:
                    password = getpass.getpass(f'Password(default ********): ') or default_pass
            else:
                password = getpass.getpass(f'Password: ')

        if not username or not password:
            return None, None

        session, access_token = self.okta_login(idp_uri, username, password)
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
                    if not os.path.exists(env_f):
                        os.makedirs(dir, exist_ok=True)
                    with open(env_f, "w") as file:
                        file.write('\n'.join(updated))

        return session, access_token

    def redirect_uri(self) -> str:
        # stgawsscpsr-c3-c3
        uri = Config().get('app.login.url', 'https://{host}/{env}/{app}/static/console/index.html').replace('{host}', self.host).replace('{env}', self.env).replace('{app}', 'c3')
        r = requests.get(uri)

        parsed_url = urlparse(r.url)
        log2(f'{r.status_code} {uri} <-> {parsed_url.hostname}...')
        if r.status_code < 200 or r.status_code > 299:
            return None

        return r.url

    def okta_login(self, idp_uri: str, username: str, password: str) -> tuple[requests.Session, str]:
        parsed_url = urlparse(idp_uri)
        query_string = parsed_url.query
        params = parse_qs(query_string)
        # print('SEAN', params)
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
            return None, None

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

            return None, None

        # not working
        # AppSession.validate_access_token(okta_host, id_token)

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

        return session, access_token

    def validate_access_token(host, access_token):
        OKTA_ORG_URL = f"https://{host}"
        oidc_config_url = f"{OKTA_ORG_URL}/oauth2/default/.well-known/openid-configuration"
        oidc_config = requests.get(oidc_config_url).json()
        print('SEAN', oidc_config)

        # if not jwt.algorithms.has_crypto:
        #     print("No crypto support for JWT, please install the cryptography dependency")
        #     return False

        # jwks_url = "https://{okta_host}/oauth2/default/v1/keys"
        # try:
        #     jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=360)
        #     signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        # except jwt.exception.PyJWTError as err:
        #     print(f"Error: {err}")
        #     return False

        # OKTA_ORG_URL = f"https://{okta_host}"
        # CLIENT_ID = params.get('client_id', [''])[0]
        # ID_TOKEN = id_token

        # # Fetch JWKS
        # oidc_config_url = f"{OKTA_ORG_URL}/oauth2/default/.well-known/openid-configuration"
        # oidc_config = requests.get(oidc_config_url).json()
        # print('SEAN', oidc_config)
        # jwks_uri = oidc_config["jwks_uri"]
        # jwks = requests.get(jwks_uri).json()

        # # Decode and verify the ID token
        # # try:
        #     # For simplicity, assuming the first key in JWKS is the correct one for now.
        #     # In a real application, you'd match the 'kid' from the ID token header.
        # public_key = jwks["keys"][0]
        # for j in jwks["keys"]:
        #     print('SEAN pk', j)

        # # jwt.algorithms.
        # public_key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key)

        # decoded_token = jwt.decode(
        #     ID_TOKEN,
        #     public_key,
        #     algorithms=["RS256"],  # Or other algorithms used by your Okta setup
        #     audience=CLIENT_ID,
        #     issuer=oidc_config["issuer"],
        #     options={}
        #     # options={"verify_exp": True, "verify_aud": True, "verify_iss": True}
        # )
        # print("ID Token decoded and validated successfully:")
        # print(decoded_token)
        # except jwt.exceptions.PyJWTError as e:
        #     print(f"ID Token validation failed: {e}")

        if not jwt.algorithms.has_crypto:
            print("No crypto support for JWT, please install the cryptography dependency")
            return False

        okta_auth_server = f"https://{host}/oauth2/default"
        jwks_url = f"{okta_auth_server}/v1/keys"
        print('SEAN', jwks_url)
        try:
            jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=360)
            signing_key = jwks_client.get_signing_key_from_jwt(access_token)
            print('SEAN key', signing_key)
            data = jwt.decode(
                access_token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=okta_auth_server,
                audience=f"vpn_auth_server",
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )
            return data
        except jwt.exceptions.PyJWTError as err:
            print(f"Error: {err}")
            return False

    def extract(form: str, pattern: re.Pattern):
        value = None

        for l in form.split('\n'):
            # <input type="hidden" name="id_token" value="..."/>
            groups = re.match(pattern, l)
            if groups:
                value = groups[1]

        return value