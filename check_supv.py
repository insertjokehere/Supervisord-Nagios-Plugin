#!/usr/bin/env python
"""
nagios plugin to monitor indivdual supervisor processes
-------------------------------------------------------

usage

::

    check_supv -p PROCESS_NAME


"""
import argparse
import os
import sys

#nagios return codes
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

SUPERV_STAT_CHECK='sudo supervisorctl status'

#supervisor states, map state to desired warning level
supervisor_states = {
    'STOPPED': OK,
    'RUNNING': OK,
    'STOPPING': WARNING,
    'STARTING': WARNING,
    'EXITED': CRITICAL,
    'BACKOFF': CRITICAL,
    'FATAL': CRITICAL,
    'UNKNOWN': CRITICAL
}

def get_status(proc_name):
    try:
        status_output = os.popen('%s %s' % (SUPERV_STAT_CHECK, proc_name)).read()
        proc_status = status_output.split()[1]
        return (status_output, supervisor_states[proc_status])
    except:
        print "CRITICAL: Could not get status of %s" % proc_name
        raise SystemExit, CRITICAL

def check_all():
    try:
        process_list = os.popen('%s' % SUPERV_STAT_CHECK).readlines()
    except:
        print "CRITICAL: Could not run %s" % (SUPERV_STAT_CHECK,)
        raise SystemExit, UNKNOWN

    worst_return_code = OK
    processes_in_error = []
    for process_line in process_list:
        process_name = process_line.split()[0]
        process_output, process_status = get_status(process_name)
        if process_status > worst_return_code:
            worst_return_code = process_status
            processes_in_error.append((process_output, process_status),)

    if worst_return_code == OK:
        print "All processes are OK"
        raise SystemExit, OK

    if processes_in_error:
        p = []
        for process_error in processes_in_error:
            lineTokens = process_error[0].split()
            msg = "%s (%s)" % (lineTokens[0], lineTokens[1])
            p.append(msg)
        print "Processes in error: %s" % (', '.join(p))
        raise SystemExit, worst_return_code


parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group(required = True)
group.add_argument('-p', '--processes-name', dest='process_name',
    help="Name of process as it appears in supervisorctl status")
group.add_argument('-a', '--all', action="store_true",
    help="List all processes and check them")

parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
    default=False)
parser.add_argument('-q', '--quiet', dest='verbose', action='store_false')

args = parser.parse_args()

if args.all:
    check_all()
elif args.process_name:
    output = get_status(args.process_name)
    print output[0]
    raise SystemExit, output[1]
else:
    print "Unknow command"
    sys.exit(0)
