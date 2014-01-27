#!/usr/bin/env python
"""
nagios plugin to monitor indivdual supervisor processes
-------------------------------------------------------

usage

::

    check_supv -p PROCESS_NAME


"""
from optparse import OptionParser
import os

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

def get_status():
    try:
        worst = OK
        worst_lines = []
        status_output = os.popen('%s' % (SUPERV_STAT_CHECK,)).readlines()
        for line in status_output:
            proc_status = line.split()[1]
            cur_status = supervisor_states[proc_status]
            if cur_status > worst:
                worst = cur_status
                worst_lines = []
                worst_lines.append(line)
            elif cur_status == worst:
                worst_lines.append(line)
        return (worst_lines, worst)
    except:
        print "CRITICAL: Could not run %s" % (SUPERV_STAT_CHECK,)
        raise SystemExit, UNKNOWN

parser = OptionParser()
parser.add_option('-p', '--processes-name', dest='proc_name',
    help="Name of process as it appears in supervisorctl status")
parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
    default=False)
parser.add_option('-q', '--quiet', dest='verbose', action='store_false')

options, args = parser.parse_args()

output = get_status()
if output[1] != 0:
    print "Failures detected for "+(' '.join([x.split()[0] for x in output[0]]))
else:
    print "All Services OK"
raise SystemExit, output[1]