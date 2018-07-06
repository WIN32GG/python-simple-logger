import logger as log
import os

@log.element('Walking through', log_entry = True)
def poc():
    for d, _,f in os.walk('/proc'):
        for i in f:
            log.set_additional_info(i)

fh = open('log.txt', 'w+')
log.set_log_file(fh)
poc()
fh.close()