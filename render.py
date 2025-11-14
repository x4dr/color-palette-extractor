import json
import os
import time
from pathlib import Path

import click

from colors.Theme import Theme


def process_file(theme:Theme, input_file, output_file):
    # Placeholder function that processes the file and writes the result to output_file
    with open(input_file, 'r') as f:
        data = f.read()
    processed_data = theme.process_template(data)
    # print("processed:\n", processed_data)
    with open(output_file, 'w') as f:
        f.write(processed_data)
    #  print(f"Processed: {input_file} -> {output_file}")


@click.command()
@click.option('--input', 'input_path', type=click.Path(exists=True), required=True, help="Input file or directory")
@click.option('--colors', type=click.File('r'), required=False, help="Load colors from a JSON file")
@click.option('--output', type=click.Path(exists=True, file_okay=False, writable=True), required=True,
              help="Target directory for processed files")
@click.option('--variables', "variables", type=str, required=False, help="variables for the template a=b;c=d;")
def main(input_path, colors, output, variables):
    colors_data = json.load(colors if colors else Path("~/.cache/cpe/colors.json").expanduser().open())
    if not variables:
        variables = ""
    variables = {
        a: b
        for line in variables.split(";")
        if line and "=" in line
        for a, b in [line.split("=", 1)]
    }
    theme = Theme(colors_data["Colors"], colors_data["Roles"], variables)

    # Check if input is a file or directory
    if os.path.isdir(input_path):
        # If directory, process all files in the folder
        for filename in os.listdir(input_path):
            input_file = os.path.join(input_path, filename)
            if os.path.isfile(input_file):
                output_file = os.path.join(output, filename)
                process_file(theme, input_file, output_file)
    else:
        # If single file, process the file
        output_file = os.path.join(output, os.path.basename(input_path))
        process_file(theme, input_path, output_file)



if __name__ == '__main__':
    main()
