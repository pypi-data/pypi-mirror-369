from copy import deepcopy
from attr import attrs, attrib

import re
import six

if six.PY3:
    from math import inf
else:
    inf = float("inf")
from typing import Tuple, List, Union


class InvalidVersion(ValueError):
    """
    An invalid version was found, users should refer to PEP 440.
    """


@attrs
class _Version(object):
    """
    1- epoch: A numeric value indicating major version transitions. For example,
        if a software project has a major structural change, the epoch value would increment (e.g., from 1 to 2).
    2- release: Represents the stable version of the software. For instance,
        if the software is in a production-ready state, it would have a release version (e.g., "2.0.1").
    3- dev: Marks versions in active development, typically indicated by appending "dev" and a
        number to the version (e.g., "2.1.0dev1" for the first development version of the upcoming release).
    4- pre: Denotes pre-release versions that are available before the stable release,
        often marked with an "a" for alpha, "b" for beta, or "rc" for release candidate
        (e.g., "2.1.0a1" for the first alpha version).
    5- post: Identifies post-release updates, usually with a "post" and a number
        (e.g., "2.1.0post1" for the first post-release update).
    6- local: Contains local-specific version information, allowing developers to add custom version
        details for their specific needs. For example, a local version may look like "2.1.0+myappbuild42.
    """

    epoch = attrib()
    release = attrib()
    dev = attrib()
    pre = attrib()
    post = attrib()
    local = attrib()


class _BaseVersion(object):
    def __init__(self, key):
        self._key = key

    def __hash__(self):
        return hash(self._key)

    def __lt__(self, other):
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)

    def _compare(self, other, method):
        if not isinstance(other, _BaseVersion):
            return NotImplemented

        return method(self._key, other._key)


class Version(_BaseVersion):
    VERSION_PATTERN = r"""
        v?
        (?:
            (?:(?P<epoch>[0-9]+)!)?                           # epoch
            (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
            (?P<pre>                                          # pre-release
                [-_\.]?
                (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
                [-_\.]?
                (?P<pre_n>[0-9]+)?
            )?
            (?P<post>                                         # post release
                (?:-(?P<post_n1>[0-9]+))
                |
                (?:
                    [-_\.]?
                    (?P<post_l>post|rev|r)
                    [-_\.]?
                    (?P<post_n2>[0-9]+)?
                )
            )?
            (?P<dev>                                          # dev release
                [-_\.]?
                (?P<dev_l>dev)
                [-_\.]?
                (?P<dev_n>[0-9]+)?
            )?
        )
        (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
    """
    _regex = re.compile(r"^\s*" + VERSION_PATTERN +
                        r"\s*$", re.VERBOSE | re.IGNORECASE)
    _local_version_separators = re.compile(r"[\._-]")

    def __init__(self, version):
        # Validate the version and parse it into pieces
        match = self._regex.search(version)
        if not match:
            raise InvalidVersion(f"Invalid version: '{version}'")
        # We consider there to be an implicit 0 in a (pre or post or dev)-release if there is
        # not a numeral associated with it.
        pre_number: int = 0
        if match.group("pre_n"):
            pre_number = int(match.group("pre_n"))
        post_number: int = 0
        if match.group("post_n1"):
            post_number = int(match.group("post_n1"))
        elif match.group("post_n2"):
            post_number = int(match.group("post_n2"))
        dev_number: int = 0
        if match.group("dev_n"):
            dev_number = int(match.group("dev_n"))

        # Store the parsed out pieces of the version
        self._version = _Version(
            epoch=int(match.group("epoch")) if match.group("epoch") else 0,
            release=tuple(int(i) for i in match.group("release").split(".")),
            pre=self._parse_letter_version(match.group("pre_l"), pre_number),
            post=self._parse_letter_version(
                match.group("post_l") or "",
                post_number,
            ),
            dev=self._parse_letter_version(
                match.group("dev_l") or "", dev_number),
            local=self._parse_local_version(match.group("local") or ""),
        )

        # Generate a key which will be used for sorting
        key = self._cmpkey(
            self._version.epoch,
            self._version.release,
            self._version.pre,
            self._version.post,
            self._version.dev,
            self._version.local,
        )

        super(Version, self).__init__(key)

    def __repr__(self) -> str:
        return f"<Version({repr(str(self))})>"

    def __str__(self) -> str:
        parts: List[str] = []

        # Epoch
        if self.epoch != 0:
            parts.append(f"{self.epoch}!")

        # Release segment
        parts.append(".".join(str(x) for x in self.release))

        # Pre-release
        if self.pre is not None:
            parts.append("".join(str(x) for x in self.pre))

        # Post-release
        if self.post is not None:
            parts.append(f".post{self.post}")

        # Development release
        if self.dev is not None:
            parts.append(f".dev{self.dev}")

        # Local version segment
        if self.local is not None:
            parts.append(f"+{self.local}")

        return "".join(parts)

    def get_next_version(self):
        def increment(part: Union[int, List]):
            """
            :param part:union[int,list]:
            :return:  the object's type
            """
            if isinstance(part, int):
                return part + 1
            type_ = type(part)
            part = list(part)
            if isinstance(part[-1], int):
                part[-1] += 1
            return type_(part)

        next_version = deepcopy(self)
        if next_version._version.dev:
            next_version._version.dev = increment(next_version._version.dev)
        elif next_version._version.post:
            next_version._version.post = increment(next_version._version.post)
        elif next_version._version.pre:
            next_version._version.pre = increment(next_version._version.pre)
        elif next_version._version.release:
            next_version._version.release = increment(
                next_version._version.release)
        elif next_version._version.epoch:
            next_version._version.epoch = increment(
                next_version._version.epoch)
        return next_version

    @property
    def epoch(self):
        return self._version.epoch

    @property
    def release(self):
        return self._version.release

    @property
    def pre(self):
        return self._version.pre

    @property
    def post(self):
        return self._version.post[1] if self._version.post else None

    @property
    def dev(self):
        return self._version.dev[1] if self._version.dev else None

    @property
    def local(self):
        if self._version.local:
            return ".".join(str(x) for x in self._version.local)
        else:
            return None

    @property
    def public(self):
        return str(self).split("+", 1)[0]

    @property
    def base_version(self) -> str:
        parts: List[str] = []

        # Epoch
        if self.epoch != 0:
            parts.append(f"{self.epoch}!")

        # Release segment
        parts.append(".".join(str(x) for x in self.release))

        return "".join(parts)

    @property
    def is_prerelease(self):
        return self.dev is not None or self.pre is not None

    @property
    def is_postrelease(self):
        return self.post is not None

    @property
    def is_devrelease(self):
        return self.dev is not None

    @staticmethod
    def _parse_letter_version(letter: str, number: int) -> Union[Tuple[str, int], None]:
        """
        Parse letter Version
        :param letter: str: latter examples: alpha,beta....
        :param number: int:
        :return: Union[Tuple[str, int], None]: return (letter,version) or none
        """
        if not letter and not number:
            return None
        if letter:
            # We normalize any letters to their lower case form
            letter = letter.lower()

            # We consider some words to be alternate spellings of other words and
            # in those cases we want to normalize the spellings to our preferred
            # spelling.
            if letter == "alpha":
                letter = "a"
            elif letter == "beta":
                letter = "b"
            elif letter in ["c", "pre", "preview"]:
                letter = "rc"
            elif letter in ["rev", "r"]:
                letter = "post"

            return letter, int(number)
        if not letter and number:
            # We assume if we are given a number, but we are not given a letter
            # then this is using the implicit post release syntax (e.g. 1.0-1)
            letter = "post"

        return letter, int(number)

    @classmethod
    def is_valid_version_string(cls, version_string: str) -> bool:
        """
        Check iv the version is a valide one
        :param version_string: str: version we want to check
        :return: bool: True if the version is valid

        """
        if not version_string:
            return False
        match = cls._regex.search(version_string)
        return bool(match)

    @classmethod
    def _parse_local_version(cls, local: str) -> Union[Tuple, None]:
        """
        Takes a string like abc.1.twelve and turns it into ("abc", 1, "twelve").
        :param local: str: local segment
        :return: union[tuple,non]
        """
        if local is not None:
            local_ = tuple(
                part.lower() if not part.isdigit() else int(part)
                for part in cls._local_version_separators.split(local)
            )
            if not local_ or not local_[0]:
                return None
            return local_
        return None

    @staticmethod
    def _cmpkey(epoch, release, pre, post, dev, local):
        """
        Generate a key which will be used for sorting
        :param epoch:int:  A numeric value indicating major version transitions (e.g., from 1 to 2)
        :param release: tuple(int,int,int): Represents the stable version of the software (e.g (2,0,1))
        :param pre: tuple(str, int): Denotes pre-release versions that are available before the stable release,
            often marked with an "a" for alpha,
            "b" for beta, or "rc" for release candidate (e.g., pre:(a,1) "2.1.0a1"  for the first alpha version).
        :param post: tuple(str, int) : Identifies post-release updates, usually with a "post" and a number
            (e.g., post:(post,1) "2.1.0post1" for the first post-release update).
        :param dev: tuple(str, int):Marks versions in active development (e.g., dev: (dev,1) "2.1.0dev1")
        :param local: local-specific version information, allowing developers to add custom version
        :return: tuple
        """
        # When we compare a release version, we want to compare it with all of the
        # trailing zeros removed. So we'll use a reverse the list, drop all the now
        # leading zeros until we come to something non zero, then take the rest
        # re-reverse it back into the correct order and make it a tuple and use
        # that for our sorting key.
        # release = tuple(
        #     reversed(list(itertools.dropwhile(lambda x: x == 0, reversed(release))))
        # )

        # Versions without a pre-release (except as noted above) should sort after
        # those with one.
        if not pre:
            pre = inf
        elif pre:
            pre = pre[1]

        # Versions without a post segment should sort before those with one.
        if not post:
            post = -inf
        else:
            post = post[1]

        # Versions without a development segment should sort after those with one.
        if not dev:
            dev = inf
        else:
            dev = dev[1]

        if not local:
            # Versions without a local segment should sort before those with one.
            local = inf
        else:
            # Versions with a local segment need that segment parsed to implement
            # the sorting rules in PEP440.
            # - Alpha numeric segments sort before numeric segments
            # - Alpha numeric segments sort lexicographically
            # - Numeric segments sort numerically
            # - Shorter versions sort before longer versions when the prefixes
            #   match exactly
            local = local[1]

        return epoch, release, pre, post, dev, local
