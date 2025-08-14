from walker.app_session import AppSession
from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.utils import log2

class Login(Command):
    COMMAND = 'login'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Login, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Login.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        session = None
        while not session:
            app_session: AppSession = AppSession.create('c3', 'c3')
            session = app_session.login()
            if not session:
                log2('Invalid username/password. Please try again.')

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{Login.COMMAND}\t SSO login'