import logger
from time import sleep

# @logger.console_action("Printing OK")
def wait_and_print_ok():
    input("k=?")
    input("ouio")
    input("name:")
    logger.success("OK")
    print('Normal log')

@logger.console_action("e")
def e():
    sleep(1)
 
wait_and_print_ok()

