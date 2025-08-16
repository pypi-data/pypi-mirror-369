from collections.abc import Callable
from pathlib import Path

import cv2
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.interfaces import Connection

from bagsy.std import keep_only_alpha_numerical, save_csv_with_columns


def basic_message_to_numpy(topic: str, reader: AnyReader, connections: list[Connection], output_folder: Path,
                           columns: list[str],
                           msg2array: Callable[[int, object], list[np.float64]]) -> None:
    csv_np = np.zeros((sum(map(lambda c: c.msgcount, connections)), len(columns)), dtype=np.float64)
    for index, (connection, timestamp, rawdata) in enumerate(reader.messages(connections=connections)):
        msg = reader.deserialize(rawdata, connection.msgtype)
        csv_np[index, :] = [timestamp * 1e-9, *msg2array(timestamp, msg)]

    save_csv_with_columns(csv_np,
                          columns,
                          output_folder / (keep_only_alpha_numerical(topic) + ".csv"))


def nav_sat_fix(topic: str, reader: AnyReader, connections: list[Connection], output_folder: Path) -> None:
    def msg2array(_: int, msg: object) -> list[np.float64]:
        return [msg.latitude, msg.longitude, msg.altitude]

    basic_message_to_numpy(topic, reader, connections, output_folder,
                           ["timestamp", "latitude", "longitude", "altitude"],
                           msg2array)


def std_float(topic: str, reader: AnyReader, connections: list[Connection], output_folder: Path) -> None:
    def msg2array(_: int, msg: object) -> list[np.float64]:
        return [msg.data]

    basic_message_to_numpy(topic, reader, connections, output_folder,
                           ["timestamp", "data"],
                           msg2array)


def image(topic: str, reader: AnyReader, connections: list[Connection], output_folder: Path) -> None:
    output_folder = output_folder / keep_only_alpha_numerical(topic)
    output_folder.mkdir(exist_ok=True)

    def save_image_and_metadata(timestamp: int, msg: object) -> list[np.float64]:
        img = np.array(msg.data)
        img = img.reshape((msg.height, msg.width, img.shape[0] // msg.height // msg.width))
        img_path = output_folder / (str(timestamp) + ".png")
        cv2.imwrite(str(img_path), img)
        return [msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9,
                msg.height, msg.width, img.shape[0] // msg.height // msg.width]

    basic_message_to_numpy(topic, reader, connections, output_folder,
                           ["timestamp", "header timestamp", "height", "width", "channel"],
                           save_image_and_metadata)


CONVERTERS = {
    "sensor_msgs/msg/NavSatFix": nav_sat_fix,
    "std_msgs/msg/Float32": std_float,
    "std_msgs/msg/Float64": std_float,
    "sensor_msgs/msg/Image": image,
}
