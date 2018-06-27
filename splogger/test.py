import logger
from time import sleep


@logger.spinner("Printing OK")
def wait_and_print_ok():
    logger.success("OK")
    print('ok')
    print('Normal log')
    sleep(4)
    use_tqdm()
    print('All is ok')
    sleep(4)


@logger.unformat
@logger.no_spinner
def use_tqdm():
    print("Fancy console\routput")
    sleep(2)


@logger.spinner("e")
def e():
    sleep(1)


logger.capture_std_outputs()
wait_and_print_ok()
