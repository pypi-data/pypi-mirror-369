import os
import subprocess
import sys
import argparse
from pytvpaint import george
from pytvpaint.project import Project


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='TVPaint Render Arguments'
    )
    parser.add_argument('--output-path', dest='output_path')

    values, _ = parser.parse_known_args(args)

    return [values.output_path]

OUTPUT_PATH = process_remaining_args(sys.argv)[0]

print("OUTPUT PATH = ", OUTPUT_PATH)

project = Project.current_project()
clip = project.current_clip


# lancer un rendu de clip (img sequence par défaut)
clip.export_json(OUTPUT_PATH, george.SaveFormat.PNG, folder_pattern='%3li_%ln', file_pattern='%ln.%4ii', all_images=True)

print("exported")
project.close_all(True)