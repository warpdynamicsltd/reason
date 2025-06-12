#%%
from reason.parser import ProgramParser


program_parser = ProgramParser()

program = """
take a
"""

res = program_parser(program)