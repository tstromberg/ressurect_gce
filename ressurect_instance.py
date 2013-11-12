#!/usr/bin/env python3

"""Output the gcutil command to recreate a Google Compute Engine instance.

This is useful when GCE terminates one of your instances due to a planned
maintenance period.

Usage:

  First dump the instance data to a file:

  gcutil --project stromberg-org --format json getinstance grimnir > i.json

  Then run:

  ressurect_instance.py --project stromberg-org i.json

  It will output a list of commands to execute:

  gcutil --project=stromberg-org deleteinstance grimnir
  gcutil --project=stromberg-org addinstance --machine_type=f1-micro ... grimnir
"""

import json
import optparse
import os
import sys


def generate_add_command(i):
  """Given instance data as a dict, yield command line options for creation."""
  yield 'addinstance'
  yield '--machine_type=%s' % os.path.basename(i['machineType'])

  # If gcutil errors out with "INVALID_FIELD_VALUE: Invalid value for field",
  # your kernel is no longer available. Remove --kernel and pick the best
  # option.
  yield '--kernel=%s' % os.path.basename(i['kernel'])

  # These appear in "gce getinstance", but are not yet settable.
  #yield '--on_host_maintenance=%s' % i['scheduling']['onHostMaintenance'].lower()
  #if i['scheduling']['automaticRestart']:
  #  yield '--automatic_restart'
  #else:
  #  yield '--noautomatic_restart'

  # addinstance only supports one service account at the moment.
  account = i['serviceAccounts'][0]
  yield '--service_account=%s' % account['email']
  yield '--service_account_scopes=%s' % ','.join(account['scopes'])

  yield '--zone=%s' % os.path.basename(i['zone'])
  yield '--wait_until_running'

  if i.get('canIpForward'):
    yield '--can_ip_forward'
  else:
    yield '--nocan_ip_forward'

  for disk in i['disks']:
    disk_str = disk['deviceName']
    if disk['index'] == 0:
      disk_str += ',deviceName=primarydisk'
    if disk['mode'] == 'READ_WRITE':
      disk_str += ',mode=rw'
    if disk['boot']:
      disk_str += ',boot'
    yield '--disk=%s' % disk_str

  for iface in i['networkInterfaces']:
    for config in iface['accessConfigs']:
      if 'natIP' in config:
        # gcutil may complain 'Resource not found.'
        yield '--external_ip_address=%s' % config['natIP']

  yield i['name']

if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('-p', '--project', dest='project',
                    help='Google Compute Engine project name')
  (options, args) = parser.parse_args()
  if not args or not options.project:
    print('Usage: ressurect_instance.py --project <project> <path to json>')
    sys.exit(1)

  for path in args:
    json_data = open(path).read()
    instance = json.loads(json_data)
    print('gcutil --project=%s deleteinstance %s' %
          (options.project, instance['name']))
    print('gcutil --project=%s %s' %
          (options.project, ' '.join(generate_add_command(instance))))
