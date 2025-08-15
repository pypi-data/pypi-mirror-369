# Quick and dirty mock of logging module if it's not available

class MockLogging():

    DEBUG = None
    WARN = None
    INFO = None
    ERROR = None

    def basicConfig(self, **kwargs):
        pass

    def log(self, statement, level=None):
        print (statement)

    info = log

    def debug(self, statement):
        self.log(f'DEBUG: {statement}')

    def warning(self, statement):
        self.log(f'WARNING: {statement}')

    def error(self, statement):
        self.log(f'ERROR: {statement}')

logging = MockLogging()
