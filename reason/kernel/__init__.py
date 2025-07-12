from importlib.resources import files
from reason.tools.binary import run_binary

class Kernel:
    @staticmethod
    def run(input):
        bin_path = files("reason") / "assets" / "bin" / "kernel"
        return run_binary(str(bin_path), input)