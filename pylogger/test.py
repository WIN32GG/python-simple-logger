import logger
from time import sleep

@logger.console_action("Printing OK")
def wait_and_print_ok():
    sleep(4)
    logger.success("OK")
    print('Normal log')
 
class R():

    @logger.console_action("w8")
    def g(self):
        sleep(1)

wait_and_print_ok()

