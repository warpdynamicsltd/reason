import argparse
import logging

from time import perf_counter

from reason.parser import ProgramParser
from reason.core.theory.zfc import ZFC
from reason.core.interpreter import Interpreter

logging.basicConfig(level=logging.INFO)

def get_args():
    """Entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Reason CLI - Execute a file"
    )

    # Accept any file as a positional argument
    parser.add_argument(
        "file",
        type=str,
        help="The path to the file to execute"
    )

    args = parser.parse_args()
    return args


def main():
    """Entry point for the command-line interface."""
    # Your CLI logic here
    args = get_args()
    program_parser = ProgramParser()

    with open(args.file, 'r') as f:
        code = f.read()

    program_ast_list = program_parser(code)
    interpreter = Interpreter(ZFC())

    start_time = perf_counter()
    interpreter(program_ast_list)
    end_time = perf_counter()

    print(f"proved in {end_time - start_time:.3f} seconds")

if __name__ == '__main__':
    main()
