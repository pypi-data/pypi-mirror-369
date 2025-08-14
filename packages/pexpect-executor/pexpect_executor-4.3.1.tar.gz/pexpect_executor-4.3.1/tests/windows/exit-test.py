#!/usr/bin/env python3

# Standard libraries
from sys import argv, exit as sys_exit
from time import sleep

# Result
result = int(argv[1]) if len(argv) > 1 else 0
print('Result = %s' % (result))

# Delay
if len(argv) > 2:
    sleep(int(argv[2]))
    print('Slept  = %ss' % (int(argv[2])))

# Exit
sys_exit(result)
