import pytest
from unittest.mock import patch, MagicMock
from main import CommandExecutor, exec_cmd, bash, LibsEnum, Config


def mock_command_execution():
    """Helper function to mock various command execution methods."""
    mock_subprocess = patch("main.subprocess.run").start()
    mock_subprocess.return_value = MagicMock(returncode=0, stdout='Hello, World! EXIT CODE: 0\n')

    mock_os_system = patch("os.system").start()
    mock_os_system.return_value = 0

    mock_plumbum = patch("main.local").start()
    mock_plumbum.return_value = MagicMock(returncode=0, stdout='Hello, World! EXIT CODE: 0\n')

    mock_sh = patch("main.sh.Command").start()
    mock_sh.return_value = MagicMock(returncode=0, stdout='Hello, World! EXIT CODE: 0\n')

    mock_fabric = patch("main.Connection").start()
    mock_conn = mock_fabric.return_value
    mock_conn.run.return_value = MagicMock(returncode=0, stdout='Hello, World! EXIT CODE: 0\n')

    return [mock_subprocess, mock_os_system, mock_plumbum, mock_sh, mock_fabric]


@pytest.mark.parametrize("lib",
                         [LibsEnum.SUBPROCESS, LibsEnum.OS_SYSTEM, LibsEnum.PLUMBUM, LibsEnum.SH, LibsEnum.FABRIC])
def test_exec_cmd_any(lib):
    """Test the execution of a command using various libraries."""
    executor = CommandExecutor(Config())

    mocks = mock_command_execution()

    try:
        assert executor.exec_cmd_any('echo Hello, World!', lib) == (0, 'Hello, World! EXIT CODE: 0\n')
    finally:
        for mock in mocks:
            mock.stop()


@pytest.mark.parametrize("lib",
                         [LibsEnum.SUBPROCESS, LibsEnum.OS_SYSTEM, LibsEnum.PLUMBUM, LibsEnum.SH, LibsEnum.FABRIC])
def test_bash(lib):
    """Test the bash function with different command libraries."""
    Config.COMMAND_LIBRARY = lib

    mocks = mock_command_execution()

    try:
        assert bash('echo Hello, World!') == (0, 'Hello, World! EXIT CODE: 0\n')
    finally:
        for mock in mocks:
            mock.stop()


def test_multiline_command():
    """Test execution of a multiline command."""
    command = '''
    echo Line 1
    echo Line 2
    '''
    expected_output = 'Line 1\nLine 2\n EXIT CODE: 0\n'

    with patch("main.exec_cmd") as mock_exec_cmd:
        mock_exec_cmd.return_value = (0, 'Line 1\nLine 2 EXIT CODE: 0\n')

        assert exec_cmd(command) == (0, expected_output)


def test_command_error():
    """Test handling of command execution errors."""
    with patch("main.exec_cmd", side_effect=RuntimeError("Command failed")) as mock_exec_cmd:
        with patch("main.bash", side_effect=RuntimeError("Command failed")) as mock_bash:
            with pytest.raises(RuntimeError):
                exec_cmd('cmd_not_found')

            with pytest.raises(RuntimeError):
                bash('cmd_not_found')


if __name__ == "__main__":
    pytest.main()
