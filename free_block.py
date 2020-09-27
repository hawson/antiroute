#!/usr/bin/env python3 
# Dump largest free range

import logging
import sys
import argparse
import ipaddress
import re
import socket



if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='''
Find the longest contguous range of IP addresses in a subnet (CIDR notation)"
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

    if not remaining_args:
        print('''Usage:  free_block.py <subnet>''')
        sys.exit(1)


    try:
        subnet = ipaddress.ip_network(remaining_args[0])

    except ValueError as exc:
        logging.error("Subnet [%s] doesn't look valid.", remaining_args[0])
        sys.exit(1)


    free_list = []

    for IP in subnet.hosts():
        hostname = None

        try:
            hostname, alias, ipaddr = socket.gethostbyaddr(str(IP))
            logging.info(str(IP) + ' ' + hostname)
            continue

        except socket.error:
            free_list.append(IP)
            logging.info(str(IP) + ' free')



    length = 0
    index = 0

    tmp_list = []
    max_len = 0

    for i in range(1,len(free_list)):
        pack = int(free_list[i])
        last = int(free_list[i-1])

        # sequence
        if pack == last + 1:
            length += 1

        # Skiped
        else:
            if length > max_len:
                max_len = length
                index = i - length

            length = 0


    print(str(free_list[index-1]) + ' to ' + str(free_list[index+max_len]))
    print(max_len+1)

