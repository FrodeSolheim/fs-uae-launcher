from .contextaware import ContextAware


class BaseContext(ContextAware):

    def __init__(self, main_context):
        ContextAware.__init__(self, main_context)

    @property
    def config(self):
        return self.context.config

    def set_config(self, *args):
        return self.context.config.set(*args)
