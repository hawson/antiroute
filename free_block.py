#!/usr/bin/env python3
# Dump largest free range

import logging
import sys
import argparse
import ipaddress
import re
import socket


def is_free(i):
    return free_list[hosts[i]] == 1


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""
Find the longest contguous range of IP addresses in a subnet (CIDR notation)"
"""
    )

    parser.add_argument(
        "-v", "--verbose", action="count", help="Be verbose, (multiples okay)"
    )
    parser.add_argument(
        "-s", "--sort", action="count", help="sort by largest block size"
    )
    parser.add_argument("subnet", action="store", help="Range to enumerate and count")

    try:
        parsed_options, remaining_args = parser.parse_known_args()

    except SystemExit as exc:
        print(
            """
Error parsing arguments.
""".format()
        )
        sys.exit(1)

    verbose_value = 0 if parsed_options.verbose is None else parsed_options.verbose
    LOG_LEVEL = max(1, 30 - verbose_value * 10)
    logging.basicConfig(
        format="%(asctime)-15s [%(levelname)s] %(message)s", level=LOG_LEVEL
    )

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
            free_list[IP] = 0
            logging.info(str(IP) + " " + hostname)
            continue

        except socket.error:
            free_list[IP] = 1
            logging.info(str(IP) + " free")

    first = last = None

    count = 0
    prev = 0
    indexend = 0
    indexcount = 0
    # logging.debug("ip=%s: last=%s pack=%s, delta=%s max_index=%s max_length=%s, i=%s: run_index=%s run_length=%s", free_list[i], last, pack, delta, max_index, max_length, i, run_index, run_length)

    i = 0
    free_count = 0
    free_index_start = None
    free_index_end = None

    total_count = 0

    free_subnets = []

    while i < len(hosts) - 1 and total_count < len(hosts):
        total_count += 1

        # if is_free(i):
        if free_list[hosts[i]] == 1:
            free_count += 1
            if free_index_start is None:
                free_index_start = i
                free_index_end = i
            else:
                free_index_end += 1

        else:

            if free_index_start is not None:
                logging.debug("%d-%d", free_index_start, free_index_end)

                first = hosts[free_index_start]
                last = hosts[free_index_end]
                for subsubnet in ipaddress.summarize_address_range(first, last):
                    free_subnets.append(subsubnet)

                free_index_start = None
                free_index_end = None

            else:

                pass

        i += 1

        logging.debug(
            "iterations=%d free_count=%d %s (%s)",
            total_count,
            free_count,
            hosts[i],
            free_list[hosts[i]],
        )

    if free_subnets:
        print("Sub-subnets in this range:")
        if parsed_options.sort:
            for s in sorted(free_subnets, key=lambda x: x.prefixlen, reverse=True):
                print("  " + str(s))

        else:
            for s in free_subnets:
                print("  " + str(s))
