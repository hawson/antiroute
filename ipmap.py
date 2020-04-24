#!/usr/bin/env python3 
# make an IP Map

import logging
import sys
import hilbert
import argparse
import subprocess
import ipaddress



def ping_subnet(subnet):

    base_cmd = '/usr/bin/fping -a -q -i 10 -r 1 -g'
    cmd = base_cmd.split() + [subnet]
    output = subprocess.run(cmd, stdout=subprocess.PIPE, check=False, encoding='utf-8').stdout.split('\n')

    return output




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


    if True:
        try:
            subnet = ipaddress.ip_network(remaining_args[0])

        except ValueError as exc:
            logging.error("Subnet [%s] doesn't look valid.", remaining_args[0])
            sys.exit(1)

        hilbert_curve = hilbert.Hilbert(subnet.num_addresses)

        ping_output = ping_subnet(remaining_args[0])
        logging.info(ping_output)

        for ip in ping_output:
            if not ip:
                continue
            last_quad = ip.split('.')
            logging.debug("ip=%s, lq=%s", ip, last_quad)
            hilbert_curve.setd(last_quad[3], last_quad[3])



    if False:

        if remaining_args:
            elements = int(remaining_args[0])

        pinged = map(int, remaining_args[1:])


        for ip in pinged:
            hilbert_curve.setd(ip, ip)

    hilbert_curve.print()

    

