import logger
from time import sleep

@logger.console_action("Printing OK")
def wait_and_print_ok():
    inp()
    logger.success("OK")
    sleep(4)
    print('Normal log')

@logger.no_spinner
def inp():
    input("k=?")
    input("ouio")
    input("name:")

@logger.console_action("e")
def e():
    sleep(1)
 
wait_and_print_ok()

