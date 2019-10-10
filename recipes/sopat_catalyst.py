import bpy
import os
import sys
import numpy as np
import random

C = bpy.context
D = bpy.data
R = C.scene.render

root_dir = os.path.join(os.path.dirname(D.filepath), "..")
if root_dir not in sys.path:
    sys.path.append(root_dir)

import blender.particles
import blender.scene

from recipe_utilities import Timer

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
primitive_path_dark = os.path.join(root_dir, "primitives", "sopat_catalyst", "dark.blend")

n_images = 20

for image_id in range(n_images):
    with blender.scene.TemporaryState():
        primitive_dark = blender.particles.load_primitive(primitive_path_dark)
        primitive_light = blender.particles.load_primitive(primitive_path_light)

        # Ensure reproducibility of the psd.
        random.seed(image_id)

        # Create fraction 1: dark particles
        name = "dark"
        n = 200
        d_g = 50
        sigma_g = 1.6
        particles_dark = blender.particles.generate_lognormal_fraction(primitive_dark, name, n, d_g, sigma_g)

        # Create fraction 2: light particles
        name = "light"
        n = 25
        d_g = 50
        sigma_g = 1.6
        particles_light = blender.particles.generate_lognormal_fraction(primitive_light, name, n, d_g, sigma_g)

        # Combine fractions.
        particles = particles_dark+particles_light

        # Place particles.
        n_frames = 10
        lower_space_boundaries_xyz = (-resolution[0]/2, -resolution[1]/2, -10)
        upper_space_boundaries_xyz = (resolution[0]/2, resolution[1]/2, 10)
        damping = 1
        collision_shape = "sphere"

        blender.particles.place_randomly(particles,
                                         lower_space_boundaries_xyz,
                                         upper_space_boundaries_xyz,
                                         do_random_rotation=True)

        blender.particles.relax_collisions(particles,
                                           damping,
                                           collision_shape,
                                           n_frames)

        # Render and save current image and masks.
        image_id_string = "image{:06d}".format(image_id)

        output_folder_path_base = os.path.join(root_dir, "output", "sopat", image_id_string)

        image_file_name = image_id_string + ".png"
        image_folder_path = os.path.join(output_folder_path_base, "images")
        image_file_path = os.path.join(image_folder_path, image_file_name)
        blender.scene.render_to_file(image_file_path)

        mask_folder_path = os.path.join(output_folder_path_base, "masks")
        # blender.scene.render_object_masks(particles_light, image_id_string, mask_folder_path)
        blender.scene.render_occlusion_masks(particles_light, image_id_string, mask_folder_path)
