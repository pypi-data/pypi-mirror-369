# bagSy

bagSy (pronounced [`[bagzi]`](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet)) is a python cli tool to
help in the creation, conversion and sharing of rosbags.

It was created and is maintained by the SyRRo team at
the [U2IS Laboratory (ENSTA, Paris campus)](http://u2is.ensta-paris.fr/).

## Installation

It is recommended to use [pipx](https://github.com/pypa/pipx). With pipx, to install do `pipx install bagsy`.

Otherwise, you can install it in a python virtual environment.

## Usage

- `bagsy info [PATH ...]` (alias: `bag-info`): Same as rosbag info without requiring installing ros on the system.
- `bagsy convert PATH [-t topic_name ...] [-o output_folder]` (alias: `bag-convert`): Convert rosbag to csv or raw
  files depending on the message type.

## Contributions

Contributions are welcomed, consider submitting issues and/or merge requests.

## License

See [LICENSE](LICENSE)