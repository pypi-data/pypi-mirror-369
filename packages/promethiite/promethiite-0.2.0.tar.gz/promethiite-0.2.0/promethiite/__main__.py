#!/usr/bin/env python3
"""
Promethiite ingests Prometheus metrics, converts them to Graphite metrics, and
sends them to a configured Graphite server over TCP
"""

import argparse
import logging
import sys

import graphyte  # type:ignore
from prometheus_client.parser import text_string_to_metric_families


def parse_args(argv=None) -> argparse.Namespace:
    """Parse args"""

    usage_examples: str = """examples:

        %(prog)s <args>
    """
    descr: str = """
        Ingests Prometheus metrics, converts them to Graphite metrics, and
        sends them to a configured Graphite server over TCP
        """
    parser = argparse.ArgumentParser(
        description=descr,
        epilog=usage_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--file",
        "-f",
        dest="file_path",
        help=("A file path from which to get the stats. By defaults expects STDIN"),
        type=str,
    )

    parser.add_argument(
        "--prefix",
        "-p",
        help=("Value to prepend to the value name on send to Graphite"),
        required=True,
        type=str,
    )

    parser.add_argument(
        "--server",
        "-s",
        help="Graphite server",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--port",
        "-o",
        default=2003,
        help="Graphite server port",
        type=int,
    )

    parser.add_argument(
        "--proto",
        "-r",
        choices=["tcp", "udp"],
        default="tcp",
        help="Protocol to use to reach the Graphite server",
        type=str,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        dest="verbosity",
        help="Set output verbosity (-v=warning, -vv=debug)",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(argv) if argv else parser.parse_args()

    if args.verbosity >= 2:
        log_level = logging.DEBUG
    elif args.verbosity >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level)

    return args


def main():
    """Main"""

    args = parse_args(sys.argv[1:])
    logging.debug("Argparse results: %s", args)

    graphyte.init(
        args.server,
        port=args.port,
        prefix=args.prefix.replace(".", "_"),
        raise_send_errors=True,
    )

    raw_metrics: str
    if args.file_path:
        logging.info("Taking input stats from file `%s`", args.file_path)
        with open(args.file_path, mode="r", encoding="utf-8") as gfile:
            raw_metrics = gfile.read()
    else:
        logging.info("Taking input stats from STDIN")
        raw_metrics = sys.stdin.read()
    logging.debug("Ingested metrics: `%s`", raw_metrics)
    scraped_metric_count: int = 0
    sent_metric_count: int = 0
    for family in text_string_to_metric_families(raw_metrics):
        for sample in family.samples:
            scraped_metric_count += 1
            base_name = sample.name
            labels = {k: v.replace(" ", "_") for k, v in sample.labels.items()}
            name: str
            value = sample.value
            label: str = ".".join(f"{k}.{v}" for k, v in labels.items())
            name = ".".join([base_name, label])
            logging.debug("Sending Prometheus stat `%s %s` to Graphite", name, value)
            graphyte.send(name, value)
            sent_metric_count += 1
    logging.info("%s metrics scraped from Prometheus input", scraped_metric_count)
    logging.info("%s metrics sent to Graphite server", sent_metric_count)
    if scraped_metric_count != sent_metric_count:
        print(
            "Something went wrong - unable to convert and send all metrics",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
