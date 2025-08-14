# BSD 3-Clause License
#
# Copyright (c) 2022-2025, rd2
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Python implementation of the OSlg logger, in support of the OpenStudio SDK.

Original Ruby implementation/documentation: https://github.com/rd2/oslg
"""

import inspect

from dataclasses import dataclass

@dataclass(frozen=True)
class _CN:
    """
    OSlg constants (int): 'DEBUG', 'INFO', 'WARN', 'ERROR' & 'FATAL'.

    Typical usage:

        import oslg
        print(oslg.CN.FATAL)
            (-> 6)
    """
    DEBUG = 1
    INFO  = 2
    WARN  = 3
    ERROR = 4
    FATAL = 5
CN = _CN()

_tag = ("",
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "FATAL")

_msg = ("",
        "Debugging ...",
        "Success! No errors, no warnings",
        "Partial success, raised non-fatal warnings",
        "Partial success, encountered non-fatal errors",
        "Failure, triggered fatal errors")

_logs   = []
_level  = CN.INFO
_status = 0


def trim(txt="", sz=None) -> str:
    """
    Converts an object to a string. Strips if necessary.

    Args:
        txt (str):
            An object.
        sz (int):
            Selected maximum string length, or 'size' (optional).

    Returns:
        str: Stripped, trimmed string.
        "": If 'txt' cannot be converted to a valid string.

    """
    try:
        txt = str(txt).strip()
    except:
        txt = ""

    try:
        sz = int(sz)
        if len(txt) > sz: txt = txt[:sz] + " ..."
    except:
        pass

    return txt


def logs() -> list:
    """Returns generated logs."""
    return _logs


def level() -> int:
    """Returns current log level."""
    return _level


def status() -> int:
    """Returns current log status."""
    return _status


def is_debug() -> bool:
    """Returns whether current status is DEBUG."""
    return bool(_status == CN.DEBUG)


def is_info() -> bool:
    """Returns whether current status is INFO."""
    return bool(_status == CN.INFO)


def is_warn() -> bool:
    """Returns whether current status is WARNING."""
    return bool(_status == CN.WARN)


def is_error() -> bool:
    """Returns whether current status is ERROR."""
    return bool(_status == CN.ERROR)


def is_fatal() -> bool:
    """Returns whether current status is FATAL."""
    return bool(_status == CN.FATAL)


def tag(lvl=_level) -> str:
    """
    Returns a preset string that matches a log level.

    Args:
        lvl (int):
            Selected log level (e.g. CN.DEBUG).

    Returns:
        str: Matching 'tag' string (e.g. "DEBUG").
        "": If 'lvl' not an OSlg constant.

    """
    try:
        lvl = int(lvl)
    except:
        return _tag[0]

    if not 0 <= lvl < len(_tag):
        return _tag[0]

    return _tag[lvl]


def msg(stat=_status) -> str:
    """
    Returns a preset string that matches a log status.

    Args:
        stat (int):
            Selected log status (e.g. CN.FATAL).

    Returns:
        str: Matching 'status' string (e.g. "Failure, triggered fatal errors").
        "": If 'stat' not a valid OSlg constant.

    """
    try:
        stat = int(stat)
    except:
        return _msg[0]

    if not 0 <= stat < len(_msg):
        return _msg[0]

    return _msg[stat]


def reset(lvl=CN.DEBUG) -> int:
    """
    Resets log level.

    Args:
        lvl (int):
            Selected log level (e.g. CN.DEBUG).

    Returns:
        int: Newly reset log level. Remains unchanged if 'lvl' cannot be
        converted to an integer, or if not an OSlg constant (once converted).

    """
    global _level

    try:
        lvl = int(lvl)
    except:
        return _level

    if CN.DEBUG <= lvl <= CN.FATAL:
        _level = lvl

    return _level


def log(lvl=CN.DEBUG, message="", sz=None) -> int:
    """
    Logs a new entry. Overall log status is raised if new level is greater
    (e.g. FATAL > ERROR). Candidate log entry is ignored and status remains
    unchanged if the new level cannot be converted to an integer, or if not an
    OSlg constant (once converted). Relies on OSlg method 'trim()': candidate
    entry is ignored and status unchanged if message is not a valid string.

    Args:
        lvl (int):
            Selected log level (e.g. CN.DEBUG).
        message (str):
            Selected log message.
        sz (int):
            Selected maximum string length, or 'size' (optional).

    Returns:
        Current log status, potentially raised.

    """
    global _status
    global _logs

    try:
        lvl = int(lvl)
    except:
        return _status

    message = trim(message, sz)

    if not message or lvl < CN.DEBUG or lvl > CN.FATAL or lvl < _level:
        return _status

    if lvl > _status:
        _status = lvl

    _logs.append(dict(level=lvl, message=message))

    return _status


def invalid(id="", mth="", ord=0, lvl=CN.DEBUG, res=None, sz=None):
    """
    Logs template 'invalid object' entry, based on arguments. Relies on OSlg
    method 'log()': first check out its own operation, exit conditions and
    module side effects. Candidate log entry is ignored and status remains
    unchanged if 'ord' cannot be converted to an integer. Argument 'ord' is
    ignored unless > 0.

    Args:
        id (str):
            Object identifier string (e.g. "circle radius").
        mth (str):
            Method identifier string (e.g. "circle area").
        ord (int):
            Method call parameter index (e.g. '1' if 2nd argument).
        lvl (int):
            Selected log level (e.g. CN.DEBUG).
        res:
            Selected return object (e.g. 'False', None).
        sz (int):
            Selected maximum string length, or 'size' (optional).

    Returns:
        Selected return object ('res').

    """
    id  = trim(id)
    mth = trim(mth)

    try:
        ord = int(ord)
    except:
        return res

    try:
        lvl = int(lvl)
    except:
        return res

    if not id or not mth or lvl < CN.DEBUG or lvl > CN.FATAL:
        return res

    msg = "Invalid '%s' " % (id)

    if ord > 0:
        msg += "arg #%d "  % (ord)

    msg += "(%s)" % (mth)
    log(lvl, msg, sz)

    return res


def mismatch(id="", obj=None, cl=None, mth="", lvl=CN.DEBUG, res=None, sz=None):
    """
    Logs template 'instance/class mismatch' entry, based on arguments. Relies
    on OSlg method 'log()': first check out its own operation, exit conditions
    and module side effects. Candidate log entry is ignored and status remains
    unchanged if 'obj' is an instance of 'cl'.

    Args:
        id (str):
            Object identifier string (e.g. "circle radius").
        obj:
            Mismatched object (e.g. boolean)
        cl:
            Desired target class (e.g. float)
        mth (str):
            Method identifier string (e.g. "circle area").
        lvl (int):
            Selected log level (e.g. CN.DEBUG).
        res:
            Selected return object (e.g. 'False', None).
        sz (int):
            Selected maximum string length, or 'size' (optional).

    Returns:
        Selected return object ('res').

    """
    id  = trim(id)
    mth = trim(mth)

    try:
        lvl = int(lvl)
    except:
        return res

    if not id:                  return res
    if not mth:                 return res
    if lvl < CN.DEBUG:          return res
    if lvl > CN.FATAL:          return res
    if not inspect.isclass(cl): return res
    if isinstance(obj, cl):     return res

    msg  = "'%s' %s? " % (id, type(obj).__name__)
    msg += "expecting %s (%s)" % (cl.__name__, mth)
    log(lvl, msg, sz)

    return res


def hashkey(id="", dct={}, key="", mth="", lvl=CN.DEBUG, res=None, sz=None):
    """
    Logs template 'missing hash key' entry, based on arguments. Relies on OSlg
    method 'log()': first check out its own operation, exit conditions and
    module side effects. Candidate log entry is ignored and status remains
    unchanged if 'key' is found in 'dct'.

    Args:
        id (str):
            Object identifier string (e.g. "circle radius").
        dct (dict):
            Dictionary (or Hash) to validate.
        key:
            Missing dictionary key.
        mth (str):
            Method identifier string.
        lvl (int):
            Selected log level (e.g. CN.DEBUG).
        res:
            Selected return object (e.g. 'False', None).
        sz (int):
            Selected maximum string length, or 'size' (optional).

    Returns:
        Selected return object ('res').

    """
    id  = trim(id)
    mth = trim(mth)
    ky  = trim(key)

    try:
        lvl = int(lvl)
    except:
        return res

    if not id:                    return res
    if not mth:                   return res
    if lvl < CN.DEBUG:            return res
    if lvl > CN.FATAL:            return res
    if not isinstance(dct, dict): return res
    if key in dct:                return res

    log(lvl, "Missing '%s' key in %s (%s)" % (ky, id, mth), sz)

    return res


def empty(id="", mth="", lvl=CN.DEBUG, res=None, sz=None):
    """
    Logs template 'empty' entry, based on arguments. Relies on OSlg method
    'log()': first check out its own operation, exit conditions and module side
    effects.

    Args:
        id (str):
            Object identifier string (e.g. "circle radius").
        mth (str):
            Method identifier string.
        lvl (int):
            Selected log level (e.g. CN.DEBUG).
        res:
            Selected return object (e.g. 'False', None).
        sz (int):
            Selected maximum string length, or 'size' (optional).

    Returns:
        Selected return object ('res').

    """
    id  = trim(id)
    mth = trim(mth)

    try:
        lvl = int(lvl)
    except:
        return res

    if not id:         return res
    if not mth:        return res
    if lvl < CN.DEBUG: return res
    if lvl > CN.FATAL: return res

    log(lvl, "Empty '%s' (%s)" % (id, mth), sz)

    return res


def zero(id="", mth="", lvl=CN.DEBUG, res=None, sz=None):
    """
    Logs template 'zero' entry, based on arguments. Relies on OSlg method
    'log()': first check out its own operation, exit conditions and module side
    effects.

    Args:
        id (str):
            Object identifier string (e.g. "circle radius").
        mth (str):
            Method identifier string.
        lvl (int):
            Selected log level (e.g. CN.DEBUG).
        res:
            Selected return object (e.g. 'False', None).
        sz (int):
            Selected maximum string length, or 'size' (optional).

    Returns:
        Selected return object ('res').

    """
    id  = trim(id)
    mth = trim(mth)

    try:
        lvl = int(lvl)
    except:
        return res

    if not id:         return res
    if not mth:        return res
    if lvl < CN.DEBUG: return res
    if lvl > CN.FATAL: return res

    log(lvl, "Zero '%s' (%s)" % (id, mth), sz)

    return res


def negative(id="", mth="", lvl=CN.DEBUG, res=None, sz=None):
    """
    Logs template 'negative' entry, based on arguments. Relies on OSlg method
    'log()': first check out its own operation, exit conditions and module side
    effects.

    Args:
        id (str):
            Object identifier string (e.g. "circle radius").
        mth (str):
            Method identifier string.
        lvl (int):
            Selected log level (e.g. CN.DEBUG).
        res:
            Selected return object (e.g. 'False', None).
        sz (int):
            Selected maximum string length, or 'size' (optional).

    Returns:
        Selected return object ('res').

    """
    id  = trim(id)
    mth = trim(mth)

    try:
        lvl = int(lvl)
    except:
        return res

    if not id:         return res
    if not mth:        return res
    if lvl < CN.DEBUG: return res
    if lvl > CN.FATAL: return res

    log(lvl, "Negative '%s' (%s)" % (id, mth), sz)

    return res


def clean() -> int:
    """Resets log status and entries."""
    global _status
    global _logs

    _status = 0
    _logs   = []

    return _level
