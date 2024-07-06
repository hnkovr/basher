"""MIT License
===========
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import logging
import subprocess

for _ in (0, 0):
    try:
        import sh  # noqa: F401
        from fabric import Connection  # noqa: F401
        from loguru import logger as loguru_logger  # noqa: F401
        from plumbum import local  # noqa: F401

        break
    except ImportError:
        logging.exception(
            "The required libraries are not installed. Please run `pip install -r requirements.txt`.",
        )
        del logging
        subprocess.run("sh init.sh", shell=True, check=True)  # Starting a process with a partial executable path

__all__ = "sh, Connection, loguru_logger, local".split(", ")
