from core.interpreter.shell import ShellInterpreter, ShellExecutor

if __name__ == '__main__':
    # res = ShellInterpreter().run("ls")
    # print(res)
    # res = ShellInterpreter().run("pip show numpy || pip install numpy")
    # print(res)
    # res = ShellInterpreter().run("pip show numpy")
    # print(res)

    print(ShellExecutor.run("pip install numpy", timeout=10))
