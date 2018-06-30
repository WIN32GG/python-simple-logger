from __future__ import print_function
import sys
from colorama import Fore
from datetime import datetime
import threading
from threading import Lock
from threading import Thread
from multiprocessing import Value
import itertools
from time import sleep
from time import time
import atexit
from wrapt import decorator

CROSS = "✘"
TICK = "✓"
SPINNERS = [
    ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
    ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▁'],
    ['▉', '▊', '▋', '▌', '▍', '▎', '▏', '▎', '▍', '▌', '▋', '▊'],
    ['┤', '┘', '┴', '└', '├', '┌', '┬', '┐'],
    ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
]

INFO = f'\r{Fore.LIGHTGREEN_EX}[{TICK}] {Fore.RESET}'
WARN = f'\r{Fore.YELLOW}[!] {Fore.RESET}'
ERR = f'\r{Fore.RED}[{CROSS}] {Fore.RESET}'
DEBUG = f'\r{Fore.LIGHTBLUE_EX}[i] {Fore.RESET}'
FINE = f'\r    '


def DATE(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S : ")


VERBOSE = False
CURRENT_SPINNER = 1

originalStdOut = sys.stdout
originalStdErr = sys.stderr


class ProgressActionDisplayer(object):
    def __init__(self):
        self.actions = {}
        self.lock = Lock()
        self.running = Value('i', 0)
        atexit.register(self.exit)
        Thread(target=self._action_display_target, daemon=True).start()

    def exit(self):
        # self.lock.acquire()
        if self.running.value:
            originalStdOut.write('\r\033[K\n')

    def start_action(self, action):
        thread_name = threading.current_thread().name
        self.lock.acquire()
        if thread_name not in self.actions:
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
        thread_switch_interval = 1  # in sec
        spinner_chars = SPINNERS[CURRENT_SPINNER]

        # def print_at(row, column):
        #     return f'\033[{row};{column}H'

        def make_spinner():
            return itertools.cycle(spinner_chars)

        def get_action():
            nonlocal thread_index
            self.lock.acquire()
            try:
                keys = self.actions.keys()

                if len(keys) == 0:
                    return None

                if thread_index >= len(keys):
                    thread_index = 0

                thread_name = list(keys)[thread_index]
                action_length = len(self.actions[thread_name])

                if action_length == 0:
                    return None

                # print stack top
                action = self.actions[thread_name][action_length - 1]
            finally:
                self.lock.release()

            return action

        spinner = make_spinner()
        while True:
            sleep(0.1)
            # rows, _ = os.popen('stty size', 'r').read().split()

            if last_thread_index_change + thread_switch_interval > time():
                thread_index += 1
                last_thread_index_change = time()

            action = get_action()
            if not action:
                self.running.value = 0
                continue
            self.running.value = 1

            print(
                f'\r\033[K{Fore.CYAN}{next(spinner)}{Fore.MAGENTA} {action}{Fore.RESET}',
                file=originalStdOut,
                end=' ')  # TODO depth
            # {print_at(int(rows), 5)}


class FakeStdObject(object):
    def __init__(self, std_object, print_with):
        self.std_object = std_object
        self.print_with = print_with

    def write(self, obj):
        if obj == '\n':
            return

        if not obj.endswith('\n'):
            obj += '\n'

        self.print_with(obj, self.std_object, '')
        self.flush()

    def flush(self):
        self.std_object.flush()


displayer = ProgressActionDisplayer()


def set_verbose(verbose):
    global VERBOSE
    VERBOSE = verbose


def get_verbose():
    global VERBOSE
    return VERBOSE


def fine(msg, file=originalStdOut, end='\n'):
    print(f'{FINE}{DATE()}{msg}', file=file, end=end)


def success(msg, file=originalStdOut, end='\n'):
    print(f'{INFO}{DATE()}{msg}', file=file, end=end)


def warning(msg, file=originalStdOut, end='\n'):
    print(f'{WARN}{DATE()}{msg}', file=file, end=end)


def error(msg, file=originalStdErr, end='\n'):
    print(f'{ERR}{DATE()}{msg}', file=file, end=end)


def debug(msg, file=originalStdOut, end='\n'):
    global VERBOSE
    if VERBOSE:
        print(f'{DEBUG}{DATE()}{msg}', file=file, end=end)


std_captured = False


def capture_std_outputs(value=True):
    global std_captured
    if std_captured and not value:
        sys.stdout = originalStdOut
        sys.stderr = originalStdErr
        std_captured = False
        return

    if not std_captured and value:
        sys.stdout = FakeStdObject(originalStdOut, fine)
        sys.stderr = FakeStdObject(originalStdErr, error)
        std_captured = True
        return

# decorators


def no_spinner():
    @decorator
    def wrapper(func, instance, args, kwargs):  # FIXME change to ()
        try:
            displayer.start_action(None)
            return func(*args, **kwargs)
        except BaseException as e:
            raise e
        finally:
            displayer.finish_action()
    return wrapper


def unformat():
    @decorator
    def wrapper(func, instance, args, kwargs):
        global std_captured
        v = std_captured
        try:
            if v:
                capture_std_outputs(False)
            return func(*args, **kwargs)
        except BaseException as ex:
            raise ex
        finally:
            capture_std_outputs(v)
    return wrapper


# The console wrapper, show the current action while
# the function is executed
def element(action="", log_entry=False, print_exception=False):
    @decorator
    def wrapper(func, instance, args, kwargs):
        try:
            if log_entry:
                success(f'Starting: {action}')  # TODO depth (by thread)
            displayer.start_action(action)
            result = func(*args, **kwargs)
            if log_entry:
                success(f'Completed: {action}')
        except BaseException as ex:
            # displayer.lock.acquire()
            error(f'Failed: {action}: {ex.__class__.__name__}')
            # if print_exception:
            #     error("TODO : print stack") # TODO
            # displayer.lock.release()
            raise ex
        finally:
            displayer.finish_action()

        return result
    return wrapper


def clear():
    @decorator
    @unformat()
    @no_spinner()
    def wrapper(func, instance, args, kwargs):
        return func(*args, **kwargs)
    return wrapper


def fancy_output(action="", log_entry=False, print_exception=False):
    @decorator
    @element(action, log_entry, print_exception)
    def wrapper(func, instance, args, kwargs):
        return func(*args, **kwargs)
    return wrapper


def auto(log_entry=True, print_exception=True):
    @decorator
    def wrapper(func, instance, args, kwargs):
        @element(func.__name__, log_entry, print_exception)
        def wrapper2(func, instance, args, kwargs):
            return func(*args, **kwargs)
        return wrapper2(func, instance, args, kwargs)
    return wrapper


def use_spinner(index):
    global SPINNERS
    global CURRENT_SPINNER
    assert index > 0 and index < len(SPINNERS)
    CURRENT_SPINNER = index


__all__ = [
    "auto",
    "clear",
    "use_spinner",
    "element",
    "no_spinner",
    "capture_std_outputs",
    "success",
    "error",
    "debug",
    "warning",
    "get_verbose",
    "set_verbose",
    "fine",
    "unformat"]
