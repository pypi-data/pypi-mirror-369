import os
import signal
import traceback

from walker.app_session import AppSession, IdpLogin
from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.utils import log2

class UserEntry(Command):
    COMMAND = 'entry'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(UserEntry, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return UserEntry.COMMAND

    def run(self, cmd: str, state: ReplState):
        def custom_handler(signum, frame):
            AppSession.ctrl_c_entered = True

        signal.signal(signal.SIGINT, custom_handler)

        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        login: IdpLogin = None
        while not login:
            try:
                app_session: AppSession = AppSession.create('c3', 'c3')
                login = app_session.login_to_idp(use_cached=False)
                if not login:
                    log2('Invalid username/password. Please try again.')
            except:
                log2(traceback.format_exc())
                pass

        username = login.user.split('@')[0].replace('.', '')
        os.system(f'{os.getcwd()}/login.sh {username} {login.ser()}')

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{UserEntry.COMMAND}\t user entry'