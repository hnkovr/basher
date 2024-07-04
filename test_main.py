# test_main.py
import pytest

from main import CommandExecutor, Config, LibsEnum, bash, exec_cmd


@pytest.mark.parametrize("lib", [LibsEnum.SUBPROCESS, LibsEnum.OS_SYSTEM, LibsEnum.PLUMBUM, LibsEnum.SH, LibsEnum.FABRIC])
def test_exec_cmd(lib):
    Config.COMMAND_LIBRARY = lib
    assert exec_cmd("echo Hello, World!") == (0, "Hello, World! EXIT CODE: 0\n")
    assert exec_cmd(["echo", "Hello, World!"]) == (0, "Hello, World! EXIT CODE: 0\n")

@pytest.mark.parametrize("lib", [LibsEnum.SUBPROCESS, LibsEnum.OS_SYSTEM, LibsEnum.PLUMBUM, LibsEnum.SH, LibsEnum.FABRIC])
def test_exec_cmd_any(lib):
    executor = CommandExecutor(Config())
    assert executor.exec_cmd_any("echo Hello, World!", lib) == (0, "Hello, World! EXIT CODE: 0\n")
    assert executor.exec_cmd_any(["echo", "Hello, World!"], lib) == (0, "Hello, World! EXIT CODE: 0\n")

@pytest.mark.parametrize("lib", [LibsEnum.SUBPROCESS, LibsEnum.OS_SYSTEM, LibsEnum.PLUMBUM, LibsEnum.SH, LibsEnum.FABRIC])
def test_bash(lib):
    Config.COMMAND_LIBRARY = lib
    assert bash("echo Hello, World!") == (0, "Hello, World! EXIT CODE: 0\n")
    assert bash(["echo", "Hello, World!"]) == (0, "Hello, World! EXIT CODE: 0\n")

def test_multiline_command():
    command = """
    echo Line 1
    echo Line 2
    """
    expected_output = "Line 1\nLine 2\n EXIT CODE: 0\n"
    assert exec_cmd(command) == (0, expected_output)
    assert bash(command) == (0, expected_output)

def test_command_error():
    with pytest.raises(RuntimeError):
        exec_cmd("cmd_not_found")

    with pytest.raises(RuntimeError):
        bash("cmd_not_found")

if __name__ == "__main__":
    pytest.main()
