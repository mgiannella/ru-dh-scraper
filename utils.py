from datetime import datetime
from colorama import init, Fore
import sys

def get_date_logging():
    return str(datetime.now())[11:][:-3]

class Logger: 
    def __init__(self, filename = None): 
        init(autoreset=True)
        #if no  filename is included as a string, it assumes you don't want to create a log file
        if filename == None:
            self.logToTxt = False
        else:
            self.logToTxt = True
            self.filename = filename

    def write2file(self,text):
        with open(self.filename, "a") as f:
            f.write(text)

    def success(self, message):
        sys.stdout.write(Fore.GREEN + "["+ get_date_logging()+"] " + message + '\n')
        sys.stdout.flush()
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + "SUCCESS: " + message + '\n')

    def warn(self, message):
        sys.stdout.write(Fore.YELLOW + "["+ get_date_logging()+"] " + message + '\n')
        sys.stdout.flush()
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + "WARNING: " + message + '\n')

    def log(self, message):
        sys.stdout.write(Fore.CYAN + "["+ get_date_logging()+"] " + message + '\n')
        sys.stdout.flush()
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + message + '\n')

    def error(self, message):
        sys.stdout.write(Fore.RED + "["+ get_date_logging()+"] " + message + '\n')
        sys.stdout.flush()
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + "ERROR: " + message + '\n')

    def status(self, message):
        sys.stdout.write(Fore.MAGENTA + "["+ get_date_logging()+"] " + message + '\n')
        sys.stdout.flush()
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + "STATUS: " + message + '\n')

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
