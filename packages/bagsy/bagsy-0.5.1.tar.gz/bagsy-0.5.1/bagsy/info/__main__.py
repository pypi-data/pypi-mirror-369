import datetime as dt
import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from rosbags.highlevel import AnyReader
from rosbags.typesys import get_typestore, Stores

from bagsy.logger import setup_logging
from bagsy.parser import parse_and_exec

logger = logging.getLogger(__name__)


def rosbag_info(bag_path: Path) -> None:
    typestore = get_typestore(Stores.ROS1_NOETIC)
    with AnyReader([bag_path], default_typestore=typestore) as reader:
        logger.info(f"path:        {bag_path.name}")
        # rosbags can only read version 2.0 for ros1
        logger.info(f"version:     {'ros2' if reader.is2 else 'ros1 v2.0'}")
        logger.info(f"duration:    {(reader.end_time - reader.start_time) * 1e-9:.2f}s")
        logger.info("start:       "
                    f"{dt.datetime.fromtimestamp(reader.start_time * 1e-9).strftime('%b %d %Y %H:%M:%S.%f')}")
        logger.info(
            f"end:         {dt.datetime.fromtimestamp(reader.end_time * 1e-9).strftime('%b %d %Y %H:%M:%S.%f')}")
        logger.info(f"size:        {bag_path.stat().st_size / 1024 / 1024:.1f} Mo")
        topics = {}
        types = {}
        for connection in reader.connections:
            topics[connection.topic] = (connection.msgtype, connection.msgcount
                                        + (topics[connection.topic][1] if connection.topic in topics else 0))
            types[connection.msgtype] = connection.digest
        logger.info(f"messages:    {sum(map(lambda x: x[1], topics.values()))}")
        # TODO find api function in rosbags to get compression info
        logger.info(f"compression: not detected (not yet supported by bagSy)")
        longest_types_len = len(sorted(types.keys(), key=lambda s: len(s))[-1])
        types_str = '\n             '.join([f'{k.ljust(longest_types_len)} [{v}]' for k, v in types.items()])
        logger.info(f"types:       {types_str}")
        longest_topics_len = len(sorted(topics.keys(), key=lambda s: len(s))[-1])
        topics_str = '\n             '.join([f'{k.ljust(longest_topics_len)}'
                                             f' {str(v[1]).rjust(5)}'
                                             f' msg{"s:" if v[1] > 1 else ": "} {v[0]}' for k, v in topics.items()])
        logger.info(f"topics:      {topics_str}")


# === command line interface

def setup_parser(parser: ArgumentParser) -> None:
    parser.add_argument("bag_paths", type=Path, help="Path to the rosbag", nargs='+')


def exec_cmd(args: Namespace, _: ArgumentParser):
    first = True
    for bag_path in args.bag_paths:
        if not first:
            logger.info("---")
        else:
            first = False
        rosbag_info(bag_path)


def main(cli_args: Optional[list[str]] = None):
    setup_logging(logging.INFO)

    parse_and_exec("bagsy.info",
                   "bag-info",
                   "Same as rosbag info without requiring installing ros on the system.",
                   cli_args)


if __name__ == "__main__":
    main()
