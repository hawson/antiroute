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


    free_list = {}

    hosts = list(subnet.hosts())

    for IP in hosts:
        hostname = None

        try:
            hostname, alias, ipaddr = socket.gethostbyaddr(str(IP))
            logging.info(str(IP) + ' ' + hostname)
            free_list[IP] = 0
            continue

        except socket.error:
            free_list[IP] = 1
            logging.info(str(IP) + ' free')




    first = last = None


    count = 0
    prev = 0
    indexend = 0
    indexcount = 0
        #logging.debug("ip=%s: last=%s pack=%s, delta=%s max_index=%s max_length=%s, i=%s: run_index=%s run_length=%s", free_list[i], last, pack, delta, max_index, max_length, i, run_index, run_length)

    for i in range(len(hosts)):

        if free_list[hosts[i]] == 1:
            count += 1
            indexcount = i
        else:
            if count > prev:
                prev = count
                indexend = i
            count = 0

    if count > prev:
        prev = count -1 
        indexend = indexcount +1

    first = hosts[indexend-prev]
    last = hosts[indexend-1]

    print(str(first) + ' to ' + str(last))
    print("Count: {}".format(prev))

    print("Sub-subnets in this range:")
    if first != last:
        for subsubnet in ipaddress.summarize_address_range(first, last):
            print('  ' + str(subsubnet))
    else:
        print(str(first))

