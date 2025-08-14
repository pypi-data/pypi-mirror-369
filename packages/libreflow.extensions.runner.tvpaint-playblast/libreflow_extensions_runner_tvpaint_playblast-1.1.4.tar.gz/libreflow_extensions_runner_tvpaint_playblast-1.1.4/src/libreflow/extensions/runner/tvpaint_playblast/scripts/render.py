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
    parser.add_argument('--start-frame', dest='start_frame')
    parser.add_argument('--end-frame', dest='end_frame')
    parser.add_argument('--render-quality', dest='render_quality')
    parser.add_argument('--show-ref', dest='show_ref')

    values, _ = parser.parse_known_args(args)

    return [values.output_path,values.start_frame,values.end_frame,values.render_quality,values.show_ref]

OUTPUT_PATH = process_remaining_args(sys.argv)[0]
FRAME_START = process_remaining_args(sys.argv)[1]
FRAME_END = process_remaining_args(sys.argv)[2]
RENDER_QUALITY = process_remaining_args(sys.argv)[3]
SHOW_REF = process_remaining_args(sys.argv)[4]


project = Project.current_project()
clip = project.current_clip

if RENDER_QUALITY == "Preview":
    clip.camera.width = clip.camera.width/2
    clip.camera.height = clip.camera.height/2

    preview_width = project.width / 2
    preview_height = project.height / 2
    project = project.resize(preview_width,preview_height,overwrite = False, resize_opt = george.ResizeOption.STRETCH)
    for point in clip.camera.points:
        point.scale = point.scale * 2
    clip = next(project.clips)

# prevent frame range overshoot
if FRAME_START != "None" :
    FRAME_START = int(FRAME_START)
    if FRAME_START < clip.start :
        FRAME_START = clip.start
elif clip.mark_in is not None:
    FRAME_START = clip.mark_in
else:
    FRAME_START = project.start_frame
print (FRAME_START)


if FRAME_END != "None" :
    FRAME_END = int(FRAME_END)
    if FRAME_END > clip.end :
        FRAME_END = clip.end
elif clip.mark_out is not None: 
    FRAME_END = clip.mark_out
else:
    FRAME_END = project.end_frame
print (FRAME_END)

 
# cacher img sequence ref
if SHOW_REF == 'False':
    for layer in clip.layers:
        if "[REF]" in layer.name :
            layer.is_visible = False


# lancer un rendu de clip (img sequence par défaut)
clip.render(OUTPUT_PATH,start = FRAME_START,end = FRAME_END, use_camera = True)

print("rendered")
project.close_all(True)