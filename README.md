# Simple Python Logger

A simple tool to have nicer console output

## Features
- Easy to use success/warning/error/debug comphrensive output
- Easy to use current task information spinner

## Usage

To mark a function as 'output worthy' use the @console_output decorator
```python
    import logger
    from time import sleep

    @logger.console_action("Printing OK")
    def wait_and_print_ok():
        sleep(4)
        logger.success("OK")
        print('Normal log')

    wait_and_print_ok()
```