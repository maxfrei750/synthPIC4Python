import bpy
import os
import sys
import random
import PIL.ImageEnhance

C = bpy.context
D = bpy.data
R = C.scene.render

root_dir = os.path.join(os.path.dirname(D.filepath), "..")
if root_dir not in sys.path:
    sys.path.append(root_dir)

import blender.particles
import blender.scene

from recipe_utilities import generate_gaussian_noise_image

primitive_path = os.path.join(root_dir, "primitives", "carbon_nano_tubes_sem", "fiber.blend")
n_images = 1000

def create_fiber_fraction(primitive):
    blender.particles.hide(primitive, False)

    class_name = "fiber"
    particles = list()

    number = random.randint(1, 5)

    for particle_id in range(number):
        particle_name = class_name + "{:06d}".format(particle_id)
        particle = blender.particles.duplicate(primitive, particle_name)

        radius = random.uniform(3, 42)

        hair_length_factor = random.uniform(0.3, 1)
        blender.particles.set_hair_length_factor(particle, hair_length_factor)
        blender.particles.set_hair_radius(particle, radius)
        blender.particles.randomize_shape(particle)

        # Create a custom attribute "class". This attribute is used in the function blender.scene.save_annotation_file.
        particle["class"] = class_name

        particles.append(particle)

    blender.particles.hide(primitive)

    return particles


for image_id in range(n_images):
    with blender.scene.TemporaryState():
        # Settings
        blender.scene.apply_default_settings(engine="CYCLES")

        resolution = (1280, 960)
        blender.scene.set_resolution(resolution)

        # Generate geometry.
        primitive = blender.particles.load_primitive(primitive_path)

        # Ensure reproducibility of the psd.
        random.seed(image_id)
        particles = create_fiber_fraction(primitive)

        # Place particles.
        lower_space_boundaries_xyz = (-resolution[0] / 2, -resolution[1] / 2, -100)
        upper_space_boundaries_xyz = (resolution[0] / 2, resolution[1] / 2, 100)

        blender.particles.place_randomly(particles,
                                         lower_space_boundaries_xyz,
                                         upper_space_boundaries_xyz,
                                         do_random_rotation=True)

        # Create the individual layers that form the final image.
        particle_layer = blender.scene.render_to_variable()
        particle_layer = PIL.ImageEnhance.Contrast(particle_layer).enhance(1.5)
        particle_layer = PIL.ImageEnhance.Brightness(particle_layer).enhance(2.2)
        particle_layer = particle_layer.filter(PIL.ImageFilter.GaussianBlur(radius=1.5))

        background_layer = generate_gaussian_noise_image(resolution,
                                                         scale=200,
                                                         strength=0.1,
                                                         contrast=0.2,
                                                         brightness=0.6)

        background_noise_layer = generate_gaussian_noise_image(resolution,
                                                               scale=20,
                                                               strength=0.1,
                                                               contrast=0.2,
                                                               brightness=0.6)

        noise_layer = generate_gaussian_noise_image(resolution,
                                                    strength=0.075)

        # Compose layers.
        final_image = background_layer
        final_image = final_image = PIL.Image.blend(final_image, background_noise_layer, 0.2)
        final_image = PIL.Image.alpha_composite(final_image, particle_layer)
        final_image = PIL.Image.blend(final_image, noise_layer, 0.2)

        # # Adjust the contrast and brightness of the final image.
        # final_image = PIL.ImageEnhance.Contrast(final_image).enhance(1)
        # final_image = PIL.ImageEnhance.Brightness(final_image).enhance(1.18)

        # Save image.
        image_id_string = "image{:06d}".format(image_id)
        image_file_name = image_id_string + ".png"

        output_folder_path_base = os.path.join(root_dir, "output", "test_fibers", image_id_string)
        image_folder_path = os.path.join(output_folder_path_base, "images")
        os.makedirs(image_folder_path, exist_ok=True)

        image_file_path = os.path.join(image_folder_path, image_file_name)

        final_image = final_image.convert("L")
        final_image.save(image_file_path)

        # # Optional: Show image.
        # final_image.show()

        # Render and save masks.
        mask_folder_path = os.path.join(output_folder_path_base, "masks")
        blender.scene.render_object_masks(particles, image_id_string, mask_folder_path)
        # blender.scene.render_occlusion_masks(particles, image_id_string, mask_folder_path)
