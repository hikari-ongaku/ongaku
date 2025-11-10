# MIT License

# Copyright (c) 2023-present MPlatypus

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Type aliases and variables."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from ongaku.client import Extension

# Types

DumpType = typing.Callable[
    [typing.Sequence[typing.Any] | typing.Mapping[str, typing.Any]],
    bytes,
]
"""The json dump type."""


LoadType = typing.Callable[
    [str | bytes],
    typing.Sequence[typing.Any] | typing.Mapping[str, typing.Any],
]
"""The json load type."""

PayloadMappingT: typing.TypeAlias = typing.Mapping[str, typing.Any] | str | bytes
"""Payload Mapping Type.

Supports string, bytes, or a mapping.
"""
PayloadSequenceT: typing.TypeAlias = typing.Sequence[typing.Any] | str | bytes
"""Payload Sequence Type.

Supports string, bytes, or a sequence.
"""

ExtensionT = typing.TypeVar("ExtensionT", bound="Extension")
"""Extensions.

The type variable for an extension.
"""

RequestBodyT: typing.TypeAlias = (
    typing.Mapping[str, typing.Any] | typing.Sequence[typing.Any] | str | None
)
"""Request Body.

Request body accepted parameters.
"""

# Functions

json_loads: LoadType
"""The json loader."""

json_dumps: DumpType
"""The json dumper."""


try:
    import orjson

    json_dumps = orjson.dumps
    json_loads = orjson.loads

except ModuleNotFoundError:
    import json

    def basic_json_dumps(
        obj: typing.Sequence[typing.Any] | typing.Mapping[str, typing.Any],
    ) -> bytes:
        """Encode a JSON object to a str."""
        return json.dumps(obj).encode("utf-8")

    json_dumps = basic_json_dumps

    json_loads = json.loads
