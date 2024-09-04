#!/usr/bin/env python3 
# make an IP Map

import logging
import sys
import argparse
import subprocess
import ipaddress
import re
import os

import hilbert

def ping_subnet(subnet):

    if os.path.exists('/usr/sbin/fping'):
        fping = '/usr/sbin/fping'
    else:
        fping = '/usr/bin/fping'

    base_cmd = fping + ' -a -q -i 10 -r 1 -g'
    cmd = base_cmd.split() + [subnet]
    logging.info("fping command=%s", cmd)
    output = subprocess.run(cmd, stdout=subprocess.PIPE, check=False, encoding='utf-8').stdout.split('\n')

    new_output = []
    for ip in output:
        new_output.append(re.sub(' .*$', '', ip))

    return new_output




if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='''
IP map, using hilbert curves.
''')

    parser.add_argument('-v', '--verbose', action='count', help="Be verbose, (multiples okay)")


    try:
        parsed_options, remaining_args = parser.parse_known_args()

    except SystemExit as exc:
        print('''
Error parsing arguments.
'''.format())
        sys.exit(1)

    verbose_value = 0 if parsed_options.verbose is None else parsed_options.verbose
    LOG_LEVEL = max(1, 30 - verbose_value * 10)
    logging.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s', level=LOG_LEVEL)

    logging.debug("Begin.")

    #elements = 256
    #hilbert_curve = hilbert.Hilbert(elements)

    total_ips = None
    used_ips = 0

    if True:
        try:
            subnet = ipaddress.ip_network(remaining_args[0])
            #subnet_list = list( map(lambda x: str(x),  subnet.hosts()) )
            subnet_list = list( map(lambda x: str(x),  ipaddress.IPv4Network(remaining_args[0])) )
            logging.debug(f"Subnet = {subnet}")

            total_ips = subnet.num_addresses

        except ValueError as exc:
            logging.error("Subnet [%s] doesn't look valid.", remaining_args[0])
            sys.exit(1)

        hilbert_curve = hilbert.Hilbert(subnet.num_addresses)

        logging.debug(f"Subnet = {subnet}")
        logging.debug(f"SubnetL= {subnet_list}")
        ping_output = ping_subnet(remaining_args[0])
        logging.info('ping_output = %s', ping_output)

        offset = -1

        for ip in subnet_list:

            offset += 1

            quads = ip.split('.')
            blocked_offset = offset - (offset//256) * 256
            logging.debug("ip=%s, offset=%d, blocked=%d lq=%s", ip, offset, blocked_offset, quads)

            if not ip:
                continue

            if ip not in ping_output:
                continue

            used_ips += 1

            #hilbert_curve.setd(quads[3], quads[3])
            hilbert_curve.setd(offset, quads[3])




    if False:

        if remaining_args:
            elements = int(remaining_args[0])

        pinged = map(int, remaining_args[1:])

        for ip in pinged:
            hilbert_curve.setd(ip, ip)

    hilbert_curve.print()

    print(f"{used_ips}/{total_ips} in use")
    

