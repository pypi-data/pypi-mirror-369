"""Omit from files/stdin empty and uninteresting lines"""

import sys
import re
import fileinput
import argparse

from pathlib import PurePath
from typing import Optional

class FilterMessages:

    DEFAULT_THINGS_CONSIDERED_BORING : re.Pattern = re.compile(r'''
        """
        |
        __
        |
        \#
        |
        :
        |
        \|
        |
        '
    ''', re.VERBOSE)

    def __init__(self,
                 me: Optional[str] = PurePath(__file__).stem,
                 purpose : Optional[str] = __doc__
    ) -> None:
        """"Init the show"""
        self.args = self.parse_cmd_line(me, purpose)
        self.args.boring_regex = self.DEFAULT_THINGS_CONSIDERED_BORING


    def parse_cmd_line(self, me: str, purpose: str) -> Optional[argparse.Namespace]:
        """Read options, show help"""
        try:
            parser = argparse.ArgumentParser(
                prog=me,
                description=purpose,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )
            return parser.parse_args()
        except argparse.ArgumentError as exc:
            raise ValueError('The command-line is indecipherable')


    def __call__(self) -> int:
        """Run the show"""

        with fileinput.input() as file:
            for line in file:

                # Blank and blank-looking lines we discard
                if not line.strip():
                    continue

                # Ignore lines containing items explicitly declared uninteresting
                if self.args.boring_regex.search(line):
                    continue

                # This, by definition, is interesting
                print(line, end='')

        # All good
        return 0


def __main() -> int:

    Fm = FilterMessages()
    sys.exit(Fm())


def main() -> int:
    """TOML entry point for the script"""
    try:
        sys.exit(__main())
    except Exception:
        import traceback
        print(traceback.format_exc(), file=sys.stderr, end='')
        sys.exit(2)
    except KeyboardInterrupt:
        print('\rInterrupted by user', file=sys.stderr)
        sys.exit(3)


if __name__ == '__main__':
    sys.exit(main())
