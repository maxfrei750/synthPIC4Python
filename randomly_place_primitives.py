import bpy
import os
import sys
import random

C = bpy.context
D = bpy.data
R = C.scene.render

root_dir = os.path.dirname(D.filepath)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import blender_utilities

# Force reload in case you edit the source after you first start the blender session.
import importlib
importlib.reload(blender_utilities)

from blender_utilities import *

image_id = 0
output_dir_base = "/tmp"
output_dir = os.path.join(output_dir_base)
output_filename = "image{:06d}.png".format(image_id)
output_path = os.path.join(output_dir, output_filename)

previous_file_path = D.filepath
temp_file_path = previous_file_path + "_temp"

try:
    bpy.ops.wm.save_as_mainfile(filepath=temp_file_path)

    # Set render settings.
    R.engine = 'CYCLES'
    C.scene.cycles.device = 'GPU'
    R.image_settings.color_mode = 'RGBA'
    R.image_settings.color_depth = '8'
    R.film_transparent = True

    # Create geometry.
    primitive = append_primitive("D:\\sciebo\\Dissertation\\Python\\synthPIC4Python\\primitives\\tem_bumpy_spherical.blend")

    n_particles = 10
    
    for particle_id in range(n_particles):
        particle_name = "particle"+str(particle_id)
        particle1 = duplicate_object(primitive, particle_name)

        x = random.randint(-200, 200)
        y = random.randint(-200, 200)

        particle1.location = (x, y, 0)

    # Hide primitive
    primitive.hide_viewport = True
    primitive.hide_render = True

    # Render.
    R.filepath = output_path
    bpy.ops.render.render(write_still=True)

finally:
    bpy.ops.wm.open_mainfile(filepath=previous_file_path)
    os.remove(temp_file_path)
