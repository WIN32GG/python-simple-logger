import logger as log
import os

@log.element('Walking through', log_entry = True)
def poc():
    for d, _,f in os.walk('/proc'):
        for i in f:
            log.success(i)
            log.set_additional_info(i)

poc()