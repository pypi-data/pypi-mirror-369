import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from rosbags.highlevel import AnyReader
from rosbags.typesys import get_typestore, Stores

from bagsy.convert.rosmsg import CONVERTERS
from bagsy.logger import setup_logging
from bagsy.parser import parse_and_exec
from bagsy.std import keep_only_alpha_numerical

logger = logging.getLogger(__name__)


# === command line interface

def setup_parser(parser: ArgumentParser) -> None:
    parser.add_argument("bag_path", type=Path, help="Path to rosbag")
    parser.add_argument("--output", "-o", type=Path, help="Output directory", default=None)
    parser.add_argument("--topic", "-t", type=str, help="The topics to extract", action='append')


def exec_cmd(args: Namespace, _: ArgumentParser):
    # default save location is the current folder with the name of the page as the folder
    output_path = args.output
    if output_path is None:
        output_path = Path("./") / keep_only_alpha_numerical(args.bag_path.stem)
    output_path.mkdir(exist_ok=True, parents=True)

    typestore = get_typestore(Stores.ROS1_NOETIC)
    with AnyReader([args.bag_path], default_typestore=typestore) as reader:
        types = {}
        for connection in reader.connections:
            if connection.topic in args.topic:
                logger.info(f"Found topic {connection.topic} ({connection.msgtype})")
                types[connection.topic] = connection.msgtype

        # print unknown and unconvertable topics
        unknown = list(filter(lambda x: x not in types.keys(), args.topic))
        if len(unknown) > 0:
            logger.warning(f"Unknown topics: {', '.join(unknown)}")
        no_converters = list(filter(lambda x: x[1] not in CONVERTERS.keys(), types.items()))
        if len(no_converters) > 0:
            logger.error(f"No converters for topics: {', '.join(map(lambda x: x[0], no_converters))}."
                         f"\nThey will be ignored. ")
            for topic, _ in no_converters:
                types.pop(topic)

        # extract remaining topics
        def process_topic(topic, topic_type):
            logger.info(f"Extracting {topic}...")
            # several connections can have the same name, usually /tf is a good example
            connections = [c for c in reader.connections if c.topic == topic]
            CONVERTERS[topic_type](topic, reader, connections, output_path)
            logger.info(f"Finish extracting {topic}...")

        # Can't be parallelized, rosbags lib doesn't seem to be thread safe.
        # Maybe doing all the process of topic in one for loop on reader.messages
        # could faster. But this means that a way to keep access to the numpy arrays
        # for each topic needs to be found (maybe a dict?)
        for topic, topic_type in types.items():
            process_topic(topic, topic_type)


def main(cli_args: Optional[list[str]] = None):
    setup_logging(logging.INFO)

    parse_and_exec("bagsy.convert",
                   "bag-convert",
                   "A python cli tool to help in the conversion of rosbags.",
                   cli_args)


if __name__ == "__main__":
    main()
