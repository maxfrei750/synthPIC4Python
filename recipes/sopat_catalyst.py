import random
import sys
from pathlib import Path

import bpy
import numpy as np

C = bpy.context
D = bpy.data
R = C.scene.render

root_dir = Path(D.filepath).parent.parent
# print(root_dir)
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import blender.particles  # isort:skip
import blender.scene  # isort:skip


# # Force reload in case you edit the source after you first start the blender session.
# import importlib
#
# importlib.reload(blender.particles)
# importlib.reload(blender.scene)

# Settings
blender.scene.apply_default_settings()

resolution = (1032, 825)
blender.scene.set_resolution(resolution)

primitive_path_light = (
    root_dir / "primitives" / "sopat_catalyst" / "light.blend"
)

primitive_path_dark = root_dir / "primitives" / "sopat_catalyst" / "dark.blend"


n_images = 10

rng = np.random.default_rng(42)

uniform_distribution_float = rng.uniform
uniform_distribution_integer = rng.integers

n_min_max_dark = [250, 350]
n_min_max_light = [25, 50]

d_g_min_max = [50, 70]
sigma_g_min_max = [1.3, 1.7]

for image_id in range(n_images):
    with blender.scene.TemporaryState():
        primitive_dark = blender.particles.load_primitive(primitive_path_dark)
        primitive_light = blender.particles.load_primitive(
            primitive_path_light
        )

        # Ensure reproducibility of the psd.
        random.seed(image_id)

        # Create fraction 1: dark particles
        name = "dark"
        n = uniform_distribution_integer(*n_min_max_dark)
        d_g = uniform_distribution_float(*d_g_min_max)
        sigma_g = uniform_distribution_float(*sigma_g_min_max)
        particles_dark = blender.particles.generate_lognormal_fraction(
            primitive_dark, name, n, d_g, sigma_g, particle_class="dark"
        )

        # Create fraction 2: light particles
        name = "light"
        n = uniform_distribution_integer(*n_min_max_light)
        d_g = uniform_distribution_float(*d_g_min_max)
        sigma_g = uniform_distribution_float(*sigma_g_min_max)
        particles_light = blender.particles.generate_lognormal_fraction(
            primitive_light, name, n, d_g, sigma_g, particle_class="light"
        )

        # Combine fractions.
        particles = particles_dark + particles_light

        # Place particles.
        n_frames = 10
        lower_space_boundaries_xyz = (
            -resolution[0] / 2,
            -resolution[1] / 2,
            -10,
        )
        upper_space_boundaries_xyz = (resolution[0] / 2, resolution[1] / 2, 10)
        damping = 1
        collision_shape = "sphere"

        blender.particles.place_randomly(
            particles,
            lower_space_boundaries_xyz,
            upper_space_boundaries_xyz,
            do_random_rotation=True,
        )

        blender.particles.relax_collisions(
            particles, damping, collision_shape, n_frames
        )

        # Render and save current image and masks.
        output_root = root_dir / "output" / "sopat" / "clean"

        image_file_name = f"image_{image_id}.png"
        image_file_path = output_root / image_file_name
        blender.scene.render_to_file(image_file_path)

        blender.scene.render_occlusion_masks(particles, image_id, output_root)
        # blender.scene.render_object_masks(particles, image_id, output_root)
