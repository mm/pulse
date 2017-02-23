import models

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

class DatabaseHelper(object):
    """Convenience methods for our database. Should probably be in models.py, but not tonight."""
    
    @classmethod
    def clear_token(cls, human):
        human.access_token = ""
        human.save()