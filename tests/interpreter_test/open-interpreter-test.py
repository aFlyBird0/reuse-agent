from core.open_interpreter.languages.shell import Shell
from core.open_interpreter.computer import Computer

if __name__ == '__main__':
    Shell().run('ls')
    Computer().run("shell", "echo a")