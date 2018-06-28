import logger
from time import sleep
from subprocess import check_call


@logger.element("Printing OK")
def wait_and_print_ok():
    logger.success("OK")
    print('ok')
    print(test_input())


@logger.clear
def test_input():
    input(">")
    yes()
    input("b")
    return 'y'


@logger.auto()
def yes():
    sleep(2)


@logger.auto()
def check_script():
    sleep(2)


@logger.fancy_output("Tensorflow upgrade", log_entry=True)
def use_tqdm():
    check_call(["python", "-m", "pip", "install",
                "tensorflow", "--upgrade", "--no-cache"])


@logger.element("e")
def e():
    sleep(1)


logger.capture_std_outputs()
wait_and_print_ok()
