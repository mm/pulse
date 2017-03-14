import models
import datetime

class Rainbow(object):
    """Literally just makes terminal output pretty."""
    purple = '\033[95m'
    cyan = '\033[96m'
    darkcyan = '\033[36m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    underline = '\033[4m'
    endc = '\033[0m'

class Helper(object):

    @classmethod
    def string_to_datetime(cls, string, type):
        if type == 'time':
            return datetime.datetime.strptime(string, '%H:%M:%S').time()
        elif type == 'date':
            return datetime.datetime.strptime(string, '%Y-%m-%d')