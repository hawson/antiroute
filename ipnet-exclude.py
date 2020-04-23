#!/usr/bin/env python3

import ipaddress
import argparse
import sys
import logging
import os



def unique(L):
    LS=set(L)
    return list(LS)



def parse_file(filename):
    '''read list subnet list from a file'''

    rawlist = []
    with open(filename, 'r') as fp:
        rawlist = fp.readlines()

    logging.debug("Read %d elements form %s", len(rawlist), filename)
    return list(map(lambda x: x.strip(), rawlist))



def parse_exclusions(arguments):
    '''Take a list of arguemnts from CLI, and get exclusions (parsing files if needed).'''

    exclusions = []
    final_exclusions = []
    for arg in arguments:

        logging.debug("Parsing [%s]", arg)

        # is it a file?  if so, parse it.
        if os.path.isfile(arg):
            exclusions.extend(parse_file(arg))

        else:
            exclusions.append(arg)


    logging.debug("Testing exclusions: %s", exclusions)
    for exclusion in exclusions:

        # Does it look like a subnet?
        try:
            network = ipaddress.ip_network(exclusion)
        except ValueError:
            logging.error("%s does not look like a valid subnet", exclusion)
            continue

        final_exclusions.append(network)

    return final_exclusions




def exclude_networks(supernet, exclusions):

    networks = [supernet]

    logging.debug("Starting with %s", supernet)


    # Loop over the holes we want to punch
    for exclusion in exclusions:

        logging.debug("Exclusion %s ", exclusion)

        # loop over the chunks of the IP space that are still left
        for network in networks:

            logging.debug("  Checking if %s is within %s", exclusion, network)

            if exclusion == network:
                logging.debug("  exclusion %s exactly matches chunk %s", exclusion, network)
                networks.remove(exclusion)
                continue

            if exclusion.subnet_of(network):

                logging.debug("    excluding %s from %s", exclusion, network)

                new_nets = list(network.address_exclude(exclusion))

                networks.remove(network)

                networks.extend(new_nets)
                logging.debug("    added: %s", new_nets)
                continue


    logging.debug("  final networks: %s", networks)
    return unique(networks)






if __name__ == '__main__':


    parser = argparse.ArgumentParser(
        description='''
A file or list of subnets should be passed as CLI arguments.  If an argument "looks" like a subnet, it will be treated as such (so don't name your files "1.2.3.4/24").
''')

    parser.add_argument('-v', '--verbose', action='count', help="Be verbose, (multiples okay)")
    parser.add_argument('-S', '--supernet', action='store', default='0.0.0.0/0', help="Supernet that you are excluding from (defaults to 0.0.0.0/0)")


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

    logging.debug(parsed_options)
    logging.debug(remaining_args)

    try:
        supernet = ipaddress.ip_network(parsed_options.supernet)

    except ValueError:
        logging.error("Invalid supernet passed: %s", parsed_options.supernet)
        sys.exit(1)

    logging.debug("Supernet = %s", parsed_options.supernet)


    exclusions = parse_exclusions(remaining_args)
    logging.info('Exclusions=%s', exclusions)

    final_networks = exclude_networks(supernet, exclusions)

    for net in sorted(final_networks):
        print(net)

    sys.exit(0)
