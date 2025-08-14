import signal
from walker.app_session import AppSession
from walker.commands.command import Command
from walker.k8s_utils.ingresses import Ingresses
from walker.k8s_utils.services import Services
from walker.repl_state import ReplState
from walker.utils import log, log2

class SetupFrontend(Command):
    COMMAND = 'setup-frontend'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(SetupFrontend, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return SetupFrontend.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        app_session: AppSession = AppSession.create('c3', 'c3', state.namespace)
        Services.create_service('kaqing', state.namespace, port=5678)
        Ingresses.create_ingress('kaqing', state.namespace, app_session.host, port=5678)

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{SetupFrontend.COMMAND}\t sets up frontend'