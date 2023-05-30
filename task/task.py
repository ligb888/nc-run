import logging


class Task:

    def __init__(self, code, **args):
        self.code = code
        self.args = args

    def run(self):
        logging.info(self.args)