#/usr/bin/python3

from subprocess import Popen, PIPE, STDOUT, list2cmdline, check_output
import os 
import sys # eprint
import time

def timestamp():
    return time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())

def fail_with_return_code_and_mesage(exit_code, message):                                                                     
    sys.stderr.write(message)                                                                                                           
    sys.stderr.write("\n")                                                                                                           
    exit(exit_code)

def apply_sub_to_each_output_line_until_cmd_stops(cmd, sub):
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    for line in p.stdout:
        sub(line)
    return 0

def run_shell_command_and_capture_output(cmd):
    temp = check_output(cmd, 
			universal_newlines=True,
			shell=True)
    return str(temp)
