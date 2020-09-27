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
    parser.add_argument('subnet', action='store', help="Range to enumerate and count")


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


    try:
        subnet = ipaddress.ip_network(parsed_options.subnet)

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

        logging.debug("%s %s, %s %s, %s %s", last,pack, index, max_len, i, length)
        # sequence
        if pack == last + 1:
            length += 1

        # Skiped
        else:
            if length > max_len:
                index = i - length
                max_len = length

            length = 0


    first = free_list[index-1]
    last = free_list[index+max_len-1]
    print(str(first) + ' to ' + str(last))
    print("Count: {}".format( max_len+1))

    print("Sub-subnets in this range:")
    for subsubnet in ipaddress.summarize_address_range(first, last):
        print('  ' + str(subsubnet))


