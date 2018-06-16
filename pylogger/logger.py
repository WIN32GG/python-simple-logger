from __future__ import print_function
import sys, os
from colorama import Fore
from colorama import Style
from datetime import datetime
import threading
from threading import Lock
from threading import Thread
import itertools
from time import sleep
from time import time

CROSS = "✘"
TICK = "✓"
SPINNERS = [
    ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
    ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▁'],
    ['▉', '▊', '▋', '▌', '▍', '▎', '▏', '▎', '▍', '▌', '▋', '▊'],
    ['┤', '┘', '┴', '└', '├', '┌', '┬', '┐'],
    ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
]

INFO  = f'\r{Fore.LIGHTGREEN_EX}[{TICK}] {Fore.RESET}'
WARN  = f'\r{Fore.YELLOW}[!] {Fore.RESET}'
ERR   = f'\r{Fore.RED}[{CROSS}] {Fore.RESET}'
DEBUG = f'\r{Fore.LIGHTBLUE_EX}[i] {Fore.RESET}'
FINE  = f'\r    '
DATE  = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S ")

VERBOSE = False
CURRENT_SPINNER = 1

originalStdOut = sys.stdout
originalStdErr = sys.stderr

class ProgressActionDisplayer(object):
    def __init__(self):
        self.actions = {}
        self.lock = Lock()
        Thread(target = self._action_display_target, daemon = True).start()
        

    def start_action(self, action):
        thread_name = threading.current_thread().name
        self.lock.acquire()
        if not thread_name in self.actions:
            self.actions[thread_name] = []
        self.actions[thread_name].append(action)
        self.lock.release()
        

    def finish_action(self):
        thread_name = threading.current_thread().name
        self.lock.acquire()
        self.actions[thread_name].pop()
        self.lock.release()

    def _action_display_target(self):
        thread_index = 0
        last_thread_index_change = 0
        thread_switch_interval = 1 # in sec
        spinner_chars = SPINNERS[CURRENT_SPINNER]

        # def print_at(row, column):
        #     return f'\033[{row};{column}H'

        def make_spinner():
            return itertools.cycle(spinner_chars)

        def get_action():
            nonlocal thread_index
            self.lock.acquire()
            keys = self.actions.keys()
            if len(keys) == 0:
                return None
            if thread_index >= len(keys):
                thread_index = 0
            thread_name = list(keys)[thread_index]
            action =  self.actions[thread_name][len(self.actions[thread_name]) -1]
            self.lock.release()
            return action

        spinner = make_spinner()
        while True:
            sleep(0.1)
            #rows, _ = os.popen('stty size', 'r').read().split()
            
            if last_thread_index_change + thread_switch_interval > time():
                thread_index += 1
                last_thread_index_change = time()

            action = get_action()
            if not action:
                continue

            print(f'\r  {Fore.CYAN}{next(spinner)}{Fore.MAGENTA} {action}...{Fore.RESET}', file = originalStdOut, end='') # TODO depth
            # {print_at(int(rows), 5)}

class FakeStdObject(object):
    def __init__(self, std_object, print_with):
        self.std_object = std_object
        self.print_with = print_with

    def write(self, obj):
        self.print_with(obj, self.std_object, '')   

    def flush(self):
        self.std_object.flush()


displayer = ProgressActionDisplayer()

def setVerbose(verbose):
    global VERBOSE
    VERBOSE = verbose

def fix_msg(msg):
    if not msg.endswith('\n'):
        msg += '\n'
    return msg

def fine(msg, file = originalStdOut, end = '\n'):
    #msg = fix_msg(msg)
    print(f'{FINE}{DATE()}{msg}', file = file, end = end)

def success(msg, file = originalStdOut, end = '\n'):
    #msg = fix_msg(msg)
    print(f'{INFO}{DATE()}{msg}', file = file, end = end)

def warning(msg, file = originalStdOut, end = '\n'):
    #msg = fix_msg(msg)
    print(f'{WARN}{DATE()}{msg}', file = file, end = end)

def error(msg, file = originalStdErr, end = '\n'):
    #msg = fix_msg(msg)
    print(f'{ERR}{DATE()}{msg}', file = file, end = end)

def debug(msg, file = originalStdOut, end = '\n'):
    global VERBOSE
    if VERBOSE:
        #msg = fix_msg(msg)
        print(f'{DEBUG}{DATE()}{msg}', file = file, end = end)

sys.stdout = FakeStdObject(originalStdOut, fine)
sys.stderr = FakeStdObject(originalStdErr, error)

# The console wrapper, show the current action while
# the function is executed
def console_action(action, print_exception = False):
    def console_action_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                success(f'Started {action}') #  TODO depth (by thread)
                displayer.start_action(action)
                result = func(*args, **kwargs)
                success(f'Completed {action}')
            except BaseException as ex:
                displayer.lock.acquire()
                error(f'Failed {action}: {ex.__class__.__name__}')
                if print_exception:
                    error("TODO: print stack") # TODO
                displayer.lock.release()
                raise ex
            finally:
                
                displayer.finish_action()

            return result
        return wrapper
    return console_action_decorator  
