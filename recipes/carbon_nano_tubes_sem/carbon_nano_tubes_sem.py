import os
import random
import sys

import bpy
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

C = bpy.context
D = bpy.data
R = C.scene.render

ROOT_DIR = os.path.join(os.path.dirname(D.filepath), "..")
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import blender.particles  # isort:skip
import blender.scene  # isort:skip
from recipe_utilities import (
    generate_gaussian_noise_image,
    set_random_seed,
)  # isort:skip
from spline_utilities import calculate_spline_length  # isort:skip


def create_fiber_fraction(diameter):
    class_names = ["loop", "noloop"]
    class_weights = [1, 1]

    number_mu_sigma = [0, 0.2]
    hair_length_factor_minmax = [0.3, 1]

    num_fibers_total = int(np.ceil(np.random.lognormal(*number_mu_sigma)))

    num_fibers_loop = random.choices(
        class_names, weights=class_weights, k=num_fibers_total
    ).count("loop")

    num_fibers_noloop = num_fibers_total - num_fibers_loop

    fibers_loop = create_particle_fraction(
        "loop", num_fibers_loop, diameter, hair_length_factor_minmax
    )

    fibers_noloop = create_particle_fraction(
        "noloop", num_fibers_noloop, diameter, hair_length_factor_minmax
    )

    return fibers_loop + fibers_noloop


def create_clutter_fraction(diameter):
    class_name = "clutter"
    number_min_max = [0, 2]
    hair_length_factor_minmax = [0.3, 1]

    number = np.random.randint(*number_min_max)

    return create_particle_fraction(
        class_name, number, diameter, hair_length_factor_minmax
    )


def create_particle_fraction(
    class_name, number, diameter, hair_length_factor_minmax
):
    primitive = load_primitive(class_name)
    blender.particles.show(primitive)

    particles = list()

    for particle_id in range(number):
        diameter *= np.random.uniform(0.8, 1.2)

        particle_name = class_name + "{:06d}".format(particle_id)
        particle = blender.particles.duplicate(primitive, particle_name)

        hair_length_factor = random.uniform(*hair_length_factor_minmax)
        blender.particles.set_hair_length_factor(particle, hair_length_factor)
        blender.particles.set_hair_diameter(particle, diameter)
        blender.particles.randomize_shape(particle)
        blender.particles.rotate_randomly(particle)

        particle["class"] = class_name

        particles.append(particle)
    blender.particles.hide(primitive)
    return particles


def generate_samples(num_images, output_folder_path, resolution):
    for image_id in range(num_images):
        set_random_seed(image_id)

        with blender.scene.TemporaryState():
            setup_scene(resolution)
            particles = create_geometry(resolution)
            image = render_image(resolution)
            save_output_data(
                image, image_id, output_folder_path, particles, resolution,
            )


def save_output_data(
    image, image_id, output_folder_path, particles_fiber, resolution
):
    os.makedirs(output_folder_path, exist_ok=True)
    image_id_string = f"synthetic{image_id:06d}"
    save_image(image, output_folder_path, image_id_string)
    blender.scene.save_spline_data(
        particles_fiber, output_folder_path, image_id_string, resolution,
    )


def render_image(resolution):
    (
        background_layer,
        background_noise_layer,
        noise_layer,
        particle_layer,
    ) = create_image_layers(resolution)
    final_image = compose_layers(
        background_layer, background_noise_layer, noise_layer, particle_layer,
    )
    return final_image


def place_clutter_on_fibers(particles_clutter, particles_fiber):

    num_particles_clutter = len(particles_clutter)

    if num_particles_clutter == 0:
        return

    vertices_sets = blender.particles.get_hair_spline_vertices(particles_fiber)

    fiber_lengths = [
        calculate_spline_length(vertices) for vertices in vertices_sets
    ]

    # Choose host fibers.
    host_fiber_vertices_sets = random.choices(
        vertices_sets, weights=fiber_lengths, k=num_particles_clutter
    )

    for host_fiber_vertices, particle_clutter in zip(
        host_fiber_vertices_sets, particles_clutter
    ):
        # Choose vertex.
        position = random.choice(host_fiber_vertices)

        blender.particles.place(particle_clutter, position)


def create_geometry(resolution):
    diameter_minmax = [6, 50]
    diameter = random.uniform(*diameter_minmax)

    fibers = create_fiber_fraction(diameter)
    clutter = create_clutter_fraction(diameter)

    place_fibers_randomly(fibers, resolution)

    place_clutter_on_fibers(clutter, fibers)
    return fibers


def setup_scene(resolution):
    blender.scene.apply_default_settings(engine="CYCLES")
    blender.scene.set_resolution(resolution)


def save_image(image, output_folder_path, image_id_string):
    image_file_name = image_id_string + "_image.png"
    image_file_path = os.path.join(output_folder_path, image_file_name)
    image = image.convert("L")
    image.save(image_file_path)


def compose_layers(
    background_layer, background_noise_layer, noise_layer, particle_layer
):
    final_image = background_layer
    final_image = Image.blend(final_image, background_noise_layer, 0.2)
    final_image = Image.alpha_composite(final_image, particle_layer)
    final_image = Image.blend(final_image, noise_layer, 0.2)
    return final_image


def create_image_layers(resolution):
    particle_layer = blender.scene.render_to_variable()
    particle_layer = post_process_particle_layer(particle_layer)
    background_layer = generate_gaussian_noise_image(
        resolution, scale=200, strength=0.1, contrast=0.2, brightness=0.6,
    )
    background_noise_layer = generate_gaussian_noise_image(
        resolution, scale=20, strength=0.1, contrast=0.2, brightness=0.6,
    )
    noise_layer = generate_gaussian_noise_image(resolution, strength=0.075)
    return (
        background_layer,
        background_noise_layer,
        noise_layer,
        particle_layer,
    )


def post_process_particle_layer(particle_layer):
    particle_layer = ImageEnhance.Contrast(particle_layer).enhance(1.5)
    particle_layer = ImageEnhance.Brightness(particle_layer).enhance(2.2)
    particle_layer = particle_layer.filter(
        ImageFilter.GaussianBlur(radius=1.5)
    )
    return particle_layer


def place_fibers_randomly(particles, resolution):
    (
        lower_space_boundaries_xyz,
        upper_space_boundaries_xyz,
    ) = blender.scene.get_space_boundaries(resolution)

    blender.particles.place_randomly(
        particles,
        lower_space_boundaries_xyz,
        upper_space_boundaries_xyz,
        do_random_rotation=True,
    )


def load_primitive(class_name):
    primitive_path = os.path.join(
        ROOT_DIR, "primitives", "carbon_nano_tubes_sem", f"{class_name}.blend"
    )
    primitive = blender.particles.load_primitive(primitive_path)
    return primitive


if __name__ == "__main__":
    num_images = 500
    resolution = (1280, 960)
    output_folder_path = os.path.join(
        ROOT_DIR, "output", "+clutter_+loops_+overlaps (synthetic)"
    )

    generate_samples(num_images, output_folder_path, resolution)
