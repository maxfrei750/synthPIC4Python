import bpy
import os
import sys
import numpy as np
import random

import time

C = bpy.context
D = bpy.data
R = C.scene.render

root_dir = os.path.join(os.path.dirname(D.filepath), "..")
if root_dir not in sys.path:
    sys.path.append(root_dir)

import blender.particles
import blender.scene

# # Force reload in case you edit the source after you first start the blender session.
# import importlib
#
# importlib.reload(blender.particles)
# importlib.reload(blender.scene)

# Settings
blender.scene.apply_default_settings()

resolution = (1032, 825)
blender.scene.set_resolution(resolution)


primitive_path_light = os.path.join(root_dir, "primitives", "sopat_catalyst", "light.blend")
primitive_light = blender.particles.load_primitive(primitive_path_light)

n_images = 100

for image_id in range(n_images):
    t = time.time()

    # Ensure reproducibility of the psd.
    random.seed(image_id)

    # Create fraction 1: dark particles
    name = "dark"
    n = 200
    d_g = 50
    sigma_g = 1.6
    particles_dark = generate_lognormal_fraction(primitive_dark, name, n, d_g, sigma_g)

    # Create fraction 2: light particles
    name = "light"
    n = 25
    d_g = 50
    sigma_g = 1.6
    particles_light = generate_lognormal_fraction(primitive_light, name, n, d_g, sigma_g)

    # Combine fractions.
    particles = particles_dark+particles_light

    # Place particles.
    n_frames = 10
    lower_space_boundaries_xyz = (-resolution[0]/2, -resolution[1]/2, -10)
    upper_space_boundaries_xyz = (resolution[0]/2, resolution[1]/2, 10)
    damping = 1
    collision_shape = "box"

    blender.particles.place_randomly(particles,
                                     lower_space_boundaries_xyz,
                                     upper_space_boundaries_xyz,
                                     do_random_rotation=True)

    blender.particles.relax_collisions(particles,
                                       damping,
                                       collision_shape,
                                       n_frames)

    # Render and save current image.
    output_file_name = "{:06d}.png".format(image_id)
    output_file_path = os.path.join(root_dir, "output", "sopat", output_file_name)
    blender.scene.render_to_file(output_file_path)

    # Delete all particles.
    blender.particles.delete(particles)

    print(time.time()-t)
