#!/usr/bin/env python
"""
nagios plugin to monitor indivdual/all supervisor processes
-----------------------------------------------------------

usage, to check a single process

::

    check_supv -p PROCESS_NAME

usage, to check all declared processes

::

    check_supv -a


"""
import argparse
import sys
import subprocess
import os

#nagios return codes
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

SUPERV_STAT_CHECK = ['sudo', 'supervisorctl', 'status']

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
        status_output = subprocess.check_output(SUPERV_STAT_CHECK + [proc_name]).strip()
        proc_status = status_output.split()[1]
        return status_output, proc_status
    except Exception as e:
        print "CRITICAL: Could not get status of {} - {}".format(proc_name, e)
        sys.exit(CRITICAL)


def check_all():
    try:
        process_list = subprocess.check_output(SUPERV_STAT_CHECK).strip().split('\n')
    except Exception as e:
        print "Could not run {} ({})".format(SUPERV_STAT_CHECK, e)
        sys.exit(UNKNOWN)

    worst_return_code = OK
    processes_in_error = []
    for process_line in process_list:
        process_name = process_line.split()[0]
        process_output, process_status = get_status(process_name)
        if supervisor_states[process_status] > worst_return_code:
            worst_return_code = supervisor_states[process_status]
            processes_in_error = [(process_output, process_status)]
        elif supervisor_states[process_status] == worst_return_code:
            processes_in_error.append((process_output, process_status))

    if worst_return_code == OK:
        print "All processes are OK"
        sys.exit(OK)

    if processes_in_error:
        p = []
        for process_error in processes_in_error:
            lineTokens = process_error[0].split()
            msg = "%s (%s)" % (lineTokens[0], process_error[1])
            p.append(msg)
        print "Processes in error: %s" % (', '.join(p))
        sys.exit(worst_return_code)


parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-p', '--processes-name', dest='process_name',
                   help="Name of process as it appears in supervisorctl status")
group.add_argument('-a', '--all', action="store_true",
                   help="List all processes and check them")

parser.add_argument('--warn-stopped', dest='warn_stopped', action="store_true",
                    help="Warn if any jobs are in 'STOPPED' state")

args = parser.parse_args()

if args.warn_stopped:
    supervisor_states['STOPPED'] = WARNING

if args.all:
    check_all()
elif args.process_name:
    output = get_status(args.process_name)
    print "{} - {}" .format(args.process_name, output[1])
    sys.exit(supervisor_states[output[1]])
else:
    print "Unknown command"
    sys.exit(0)
