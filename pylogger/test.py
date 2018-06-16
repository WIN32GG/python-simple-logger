import logger
from time import sleep

@logger.console_action("Wating")
def myfunction(i):
    if i == 0:
       return
    myfunction(i -1)
 
class R():

    @logger.console_action("w8")
    def g(self):
        sleep(1)

myfunction(100)

