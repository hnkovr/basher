# main.py

import logging
import os
import subprocess
import sys
import textwrap
from enum import Enum
from typing import Any, Callable, List, Tuple, Union

# Import exception handling
try:
    import sh
    from fabric import Connection
    from loguru import logger as loguru_logger
    from plumbum import local
except ImportError:
    subprocess.run("sh init.sh", shell=True, check=True)  # noqa: S607 Starting a process with a partial executable path

    import sh
    from fabric import Connection
    from loguru import logger as loguru_logger
    from plumbum import local


class LibsEnum(Enum):
    """Enum class to hold supported libraries."""

    SUBPROCESS = "subprocess"
    OS_SYSTEM = "os_system"
    PLUMBUM = "plumbum"
    SH = "sh"
    FABRIC = "fabric"


class Config:
    """Configuration class to hold defaults, constants, and globals."""

    RUN_PYTEST = False

    LOGGING_LIBRARY = "loguru"  # Default logging library
    COMMAND_LIBRARY = LibsEnum.SUBPROCESS  # Default command execution library
    COMMAND_TRACING_PREFIX = "> "
    COMMAND_RESULT_PREFIX = ": "
    COMMAND_ERROR_PREFIX = "ERROR: "
    COMMAND_EXIT_CODE_PREFIX = "EXIT CODE: "
    LOGGING_LEVEL = "TRACE"
    RESULT_LOGGING_LEVEL = "DEBUG"
    ERROR_LOGGING_LEVEL = "ERROR"
    EXIT_CODE_LOGGING_LEVEL = "DEBUG"
    ADD_NEWLINE = True  # Option to add newline after prefixes
    NUM_TABS = 1  # Number of tabs to add if text consists of newlines


LOG = None


def set_logging_library(library: str):
    """Switch logging library by monkey-patching.

    :param library: str: The name of the logging library to use ('loguru' or 'logging').
    """
    global LOG  # noqa: PLW0603 Using the global statement to update `LOG` is discouraged

    if library == "loguru":
        LOG = globals()["LOG"] = loguru_logger
        LOG.remove()
        LOG.add(
            sys.stderr,
            level=Config.LOGGING_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        )
    else:
        LOG = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)
        globals()["LOG"] = LOG


# for pytests fixing?
LOG = globals()["LOG"] = loguru_logger
LOG.remove()
LOG.add(
    sys.stderr,
    level=Config.LOGGING_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
)


def process_command(command: Union[str, list]) -> str:
    """Process a command, which could be a multiline string or a list of command arguments.

    :param command: Union[str, list]: The command to process.
    :return: str: A single string command.
    """
    return textwrap.dedent(" ".join(command) if isinstance(command, list) else command)


def log_execution(func: Callable) -> Callable:
    """Decorate to log command execution details."""

    def wrapper(command: Union[str, List[str]], *args: Any, **kwargs: Any) -> Tuple[int, str]:
        command_str = process_command(command)

        def prefix_with_tabs(prefix: str):
            return prefix + ("\t" * Config.NUM_TABS if Config.ADD_NEWLINE and "\n" in command_str else "")

        LOG.log(Config.LOGGING_LEVEL, f"{prefix_with_tabs(Config.COMMAND_TRACING_PREFIX)}{command_str}")
        exit_code, output = func(command_str, *args, **kwargs)
        output_with_exit_code = f"{output.strip()} {Config.COMMAND_EXIT_CODE_PREFIX}{exit_code}\n"

        LOG.log(
            Config.RESULT_LOGGING_LEVEL,
            f"{prefix_with_tabs(Config.COMMAND_RESULT_PREFIX)}{output_with_exit_code}",
        )
        if exit_code != 0:
            LOG.log(
                Config.ERROR_LOGGING_LEVEL,
                f"{prefix_with_tabs(Config.COMMAND_ERROR_PREFIX)}Command failed with exit code {exit_code}",
            )

        return exit_code, output_with_exit_code

    return wrapper


def tracer(trace: bool, command: str, *, by: LibsEnum):
    """Output command if trace"""
    if trace:
        LOG.trace(f"{Config.COMMAND_TRACING_PREFIX}: {command}\t\t\t<by: {by}>")


@log_execution
def exec_cmd(
    command: Union[str, list],
    trace: Union[bool, Callable, str] = True,
    skip_err: bool = False,
    by: LibsEnum = Config.COMMAND_LIBRARY,
) -> Tuple[int, str]:
    r"""Execute a bash command with logging and error handling.

    :param command: str | list: The command to execute.
    :param trace: bool | logger_func | logger_level: Trace level for logging.
    :param skip_err: bool: Whether to skip errors.
    :param by: LibsEnum: Library to use for command execution.
    :return: Tuple[int, str]: A tuple containing the exit code and the command output.
    :raises RuntimeError: If the command exits with a non-zero status (unless skip_err is True).

    >>> exec_cmd('echo Hello, World!', True)
    (0, 'Hello, World! EXIT CODE: 0\\n')

    >>> exec_cmd('cmd_not_found', True)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    RuntimeError: Command failed with exit code 127: cmd_not_found
    """
    command = process_command(command)
    result = None

    if by == LibsEnum.SUBPROCESS:
        # Use subprocess to execute the command
        result = subprocess.run(
            command,
            shell=True,  # `subprocess` call with `shell=True` identified, security issue
            text=True,
            capture_output=True,
            check=False,
        )

    elif by == LibsEnum.OS_SYSTEM:
        # Use os.system to execute the command
        exit_code = os.system(command)
        tracer(trace, command, by=by)
        result = subprocess.CompletedProcess(command, exit_code)
    elif by == LibsEnum.PLUMBUM:
        # Use plumbum to execute the command
        cmd = local[command.split()[0]]
        tracer(trace, command, by=by)
        result = cmd(*command.split()[1:])
    elif by == LibsEnum.SH:
        # Use sh to execute the command
        cmd = sh.Command(command.split()[0])
        tracer(trace, command, by=by)
        result = cmd(*command.split()[1:])
    elif by == LibsEnum.FABRIC:
        # Use fabric to execute the command on a remote host
        conn = Connection("localhost")  # Update with actual host if needed
        tracer(trace, command, by=by)
        result = conn.run(command, hide=True)

    if result is None:
        msg = "Failed to execute command"
        raise RuntimeError(msg)

    if result.returncode != 0 and not skip_err:
        msg = f"Command failed with exit code {result.returncode}: {command}"
        raise RuntimeError(msg)

    return result.returncode, result.stdout


class CommandExecutor:
    """Class to execute bash commands and log the results."""

    def __init__(self, config: Config) -> None:
        self.config = config
        set_logging_library(self.config.LOGGING_LIBRARY)

    @log_execution
    def exec_cmd(self, command: Union[str, list]) -> Tuple[int, str]:
        r"""Execute a bash command and return the exit code and output.

        :param command: str | list: The command to execute.
        :return: Tuple[int, str]: A tuple containing the exit code and the command output.
        :raises RuntimeError: If the command exits with a non-zero status.

        >>> executor = CommandExecutor(Config())
        >>> executor.exec_cmd('echo Hello, World!')
        (0, 'Hello, World! EXIT CODE: 0\n')

        >>> executor.exec_cmd('cmd_not_found')  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        RuntimeError: Command failed with exit code 127: cmd_not_found
        """
        return exec_cmd(command, True, by=self.config.COMMAND_LIBRARY)

    @log_execution
    def exec_cmd_plumbum(self, command: Union[str, list]) -> Tuple[int, str]:
        """Execute a command using plumbum.

        :param command: str | list: The command to execute.
        :return: Tuple[int, str]: A tuple containing the exit code and the command output.
        :raises RuntimeError: If the command exits with a non-zero status.
        """
        command = process_command(command)
        cmd = local[command.split()[0]]
        result = cmd(*command.split()[1:])
        return result.returncode, str(result)

    @log_execution
    def exec_cmd_sh(self, command: Union[str, list]) -> Tuple[int, str]:
        """Execute a command using sh.

        :param command: str | list: The command to execute.
        :return: Tuple[int, str]: A tuple containing the exit code and the command output.
        :raises RuntimeError: If the command exits with a non-zero status.
        """
        command = process_command(command)
        cmd = sh.Command(command.split()[0])
        result = cmd(*command.split()[1:])
        return result.exit_code, str(result)

    @log_execution
    def exec_cmd_fabric(self, host: str, command: Union[str, list]) -> Tuple[int, str]:
        """Execute a command using fabric on a remote host.

        :param host: str: The remote host to execute the command on.
        :param command: str | list: The command to execute.
        :return: Tuple[int, str]: A tuple containing the exit code and the command output.
        :raises RuntimeError: If the command exits with a non-zero status.
        """
        command = process_command(command)
        conn = Connection(host)
        result = conn.run(command, hide=True)
        return result.exited, result.stdout

    def exec_cmd_any(
        self,
        command: Union[str, list],
        by: LibsEnum,
        **kwargs: Any,
    ) -> Tuple[int, str]:
        r"""Execute a command using the specified library.

        :param command: str | list: The command to execute.
        :param by: LibsEnum: The library to use for command execution.
        :return: Tuple[int, str]: A tuple containing the exit code and the command output.
        :raises RuntimeError: If the command exits with a non-zero status.

        >>> executor = CommandExecutor(Config())
        >>> executor.exec_cmd_any('echo Hello, World!', LibsEnum.SUBPROCESS)
        (0, 'Hello, World! EXIT CODE: 0\n')
        """
        return exec_cmd(command, by=by, **kwargs)


def bash(
    command: Union[str, list],
    *,
    skip_err: bool = False,
    **kwargs: Any,
) -> Tuple[int, str]:
    r"""Wrapp function to choose the correct command executor based on Config.

    :param command: str | list: The command to execute.
    :param trace: bool | logger_func | logger_level: Trace level for logging.
    :param skip_err: bool: Whether to skip errors.
    :return: Tuple[int, str]: A tuple containing the exit code and the command output.

    >>> bash('echo Hello, World!', trace=True)
    (0, 'Hello, World! EXIT CODE: 0\n')
    """
    executor = CommandExecutor(Config())
    try:
        return executor.exec_cmd_any(command, Config.COMMAND_LIBRARY, **kwargs)
    except RuntimeError:
        if not skip_err:
            raise
        LOG.exception(f"Command failed: {command}")
        return 1, ""


if __name__ == "__main__":
    import doctest

    doctest.testmod(raise_on_error=True)

    if Config.RUN_PYTEST:
        import pytest

        pytest.main()


def demo1():
    bash(
        """
        echo 123
        echo 456
        """,
    )


if __name__ == "__main__":
    demo1()
