from commands import find_program
import os


def open_program(program_name):

    program_name = program_name.strip().lower()

    program = find_program(program_name)

    if program:

        os.startfile(program)

        return f"Opened {program_name}"

    else:

        return f"I couldn't find {program_name}"
