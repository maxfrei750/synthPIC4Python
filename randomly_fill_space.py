import bpy
import os
import sys
import numpy as np

C = bpy.context
D = bpy.data
R = C.scene.render

root_dir = os.path.dirname(D.filepath)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import blender.particles
import blender.scene

# Force reload in case you edit the source after you first start the blender session.
import importlib

importlib.reload(blender.particles)
importlib.reload(blender.scene)

from blender.particles import *
from blender.scene import *

# create cubes
n_particles = 50

particle_list = list()

for particle_id in range(n_particles):
    size = random.randint(50, 50)
    # bpy.ops.mesh.primitive_cube_add(size=size)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=size)
    particle = bpy.context.active_object
    set_smooth_shading(particle, True)
    particle_list.append(particle)

n_frames = 10
lower_space_boundaries_xyz = (-200, -200, -50)
upper_space_boundaries_xyz = (200, 200, 50)
damping = 0
collision_shape = "Sphere"

place_randomly(particle_list,
               lower_space_boundaries_xyz,
               upper_space_boundaries_xyz,
               do_random_rotation=True)

relax_collisions(particle_list,
                 damping,
                 collision_shape,
                 n_frames)
