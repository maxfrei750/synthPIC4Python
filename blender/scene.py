import os
import tempfile

import blender.particles
import bpy
import pandas as pd
from PIL import Image
from recipe_utilities import get_random_string
from spline_utilities import calculate_spline_length


class TemporaryState:
    def __init__(self):
        self.original_path = bpy.data.filepath
        self.temporary_path = (
            self.original_path + "_state_" + get_random_string()
        )

    def __enter__(self):
        bpy.ops.wm.save_as_mainfile(filepath=self.temporary_path)

    def __exit__(self, type, value, traceback):
        bpy.ops.wm.open_mainfile(filepath=self.original_path)
        os.remove(self.temporary_path)


def set_background_color(color):
    if len(color) == 3:
        color += (1,)

    world = bpy.data.worlds["World"]
    world.use_nodes = True

    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = color
    bg.inputs[1].default_value = 1.0


def set_resolution(resolution):
    bpy.context.scene.render.resolution_x = resolution[0]
    bpy.context.scene.render.resolution_y = resolution[1]

    for camera in bpy.data.cameras:
        camera.ortho_scale = max(resolution)


def enable_all_rendering_devices():
    scene = bpy.context.scene
    scene.cycles.device = "GPU"

    preferences = bpy.context.preferences
    cycles_preferences = preferences.addons["cycles"].preferences

    # Attempt to set GPU device types if available
    for compute_device_type in ["CUDA", "OPENCL", "NONE"]:
        try:
            cycles_preferences.compute_device_type = compute_device_type
            break
        except TypeError:
            pass

    # Enable all CPU and GPU devices
    for device in cycles_preferences.devices:
        device.use = True


def apply_default_settings(engine="EEVEE"):
    engine = engine.upper()

    if engine == "EEVEE":
        engine = "BLENDER_EEVEE"

    bpy.context.scene.render.engine = engine
    enable_all_rendering_devices()

    if engine == "CYCLES":
        bpy.context.scene.cycles.samples = 4
    if engine == "BLENDER_EEVEE":
        bpy.context.scene.eevee.taa_render_samples = 32

    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.image_settings.color_depth = "8"
    bpy.context.scene.render.image_settings.compression = 0

    bpy.context.scene.render.film_transparent = True

    bpy.context.scene.use_gravity = False


def setup_workbench_renderer():
    bpy.context.scene.render.image_settings.compression = 15
    bpy.context.scene.render.image_settings.color_mode = "BW"
    bpy.context.scene.render.image_settings.color_depth = "8"
    bpy.context.scene.render.use_compositing = False
    bpy.context.scene.render.use_sequencer = False
    bpy.context.scene.render.engine = "BLENDER_WORKBENCH"
    bpy.context.scene.display.shading.light = "FLAT"
    bpy.context.scene.render.film_transparent = False
    bpy.context.scene.display.render_aa = "OFF"
    bpy.context.scene.display_settings.display_device = "None"
    bpy.context.scene.render.dither_intensity = 0

    # Set black background.
    bpy.context.scene.world.use_nodes = False
    bpy.context.scene.world.color = (0, 0, 0)


def render_to_file(absolute_file_path):
    previous_path = bpy.context.scene.render.filepath
    bpy.context.scene.render.filepath = absolute_file_path
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.render.filepath = previous_path


def render_to_variable():
    temp_file_name = get_random_string() + ".png"
    temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)
    render_to_file(temp_file_path)
    image = Image.open(temp_file_path)

    return image


def save_annotation_file(annotation_file_path, particles, do_append=False):
    particles = blender.particles.ensure_iterability(particles)

    os.makedirs(os.path.dirname(annotation_file_path), exist_ok=True)

    if os.path.isfile(annotation_file_path) and not do_append:
        os.remove(annotation_file_path)

    with open(annotation_file_path, "a+") as annotation_file:
        for particle in particles:
            assert "class" in particle, (
                "You need to assign the class attribute of the particles before saving "
                "annotations:\nExample: particle['class'] = 'test'"
            )
            annotation_file.write(particle["class"] + "\n")


def render_object_masks(particles, image_id_string, absolute_output_directory):
    particles = blender.particles.ensure_iterability(particles)

    annotation_file_path = os.path.join(
        absolute_output_directory, "..", "annotations.txt"
    )
    save_annotation_file(annotation_file_path, particles)

    with TemporaryState():
        # Set render settings.
        setup_workbench_renderer()
        bpy.context.scene.display.shading.color_type = "SINGLE"
        bpy.context.scene.display.shading.single_color = (1, 1, 1)

        # Hide all meshes.
        for instance in bpy.data.objects:
            if instance.type == "MESH":
                instance.hide_render = True

        # Unhide relevant particles one by one and render them.
        for mask_id, particle in enumerate(particles):
            blender.particles.hide(particle, False)

            output_filename = image_id_string + "_mask{:06d}.png".format(
                mask_id
            )
            output_file_path = os.path.join(
                absolute_output_directory, output_filename
            )
            render_to_file(output_file_path)

            blender.particles.hide(particle)


def create_diffuse_color_material(name, color):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = color
    return material


def replace_material(instance, material):
    instance.data.materials.clear()
    instance.data.materials.append(material)


def render_occlusion_masks(
    particles, image_id_string, absolute_output_directory
):
    particles = blender.particles.ensure_iterability(particles)

    annotation_file_path = os.path.join(
        absolute_output_directory, "..", "annotations.txt"
    )
    save_annotation_file(annotation_file_path, particles)

    with TemporaryState():
        # Set render settings.
        setup_workbench_renderer()
        bpy.context.scene.display.shading.color_type = "MATERIAL"

        material_white = create_diffuse_color_material(
            "white_mask_material", (1, 1, 1, 1)
        )
        material_black = create_diffuse_color_material(
            "black_mask_material", (0, 0, 0, 1)
        )

        # Replace textures of all meshes with black texture.
        for instance in bpy.data.objects:
            if instance.type == "MESH":
                replace_material(instance, material_black)

        # Change texture of particles to white texture one by one and render them.
        for mask_id, particle in enumerate(particles):
            replace_material(particle, material_white)

            output_filename = image_id_string + "_mask{:06d}.png".format(
                mask_id
            )
            output_file_path = os.path.join(
                absolute_output_directory, output_filename
            )
            render_to_file(output_file_path)

            replace_material(particle, material_black)


def get_space_boundaries(resolution):
    lower_space_boundaries_xyz = (
        -resolution[0] / 2,
        -resolution[1] / 2,
        -100,
    )
    upper_space_boundaries_xyz = (
        resolution[0] / 2,
        resolution[1] / 2,
        100,
    )

    return lower_space_boundaries_xyz, upper_space_boundaries_xyz


def save_spline_data(
    particles, output_folder_path, image_id_string, resolution
):
    fiber_diameters, keypoint_sets = _gather_spline_data(particles)

    lower_space_boundaries_xyz, _ = get_space_boundaries(resolution)
    x_min, y_min, _ = lower_space_boundaries_xyz
    image_width, image_height = resolution

    spline_id_offset = 0

    for spline_id, (keypoints, fiber_diameter) in enumerate(
        zip(keypoint_sets, fiber_diameters)
    ):
        spline_data = _prepare_spline_data_for_saving(
            keypoints, fiber_diameter, image_width, image_height, x_min, y_min
        )

        if spline_data.empty:
            spline_id_offset -= 1
            continue

        spline_id += spline_id_offset

        _write_spline_data_to_file(
            spline_data, output_folder_path, image_id_string, spline_id
        )


def _write_spline_data_to_file(
    spline_data, output_folder_path, image_id_string, spline_id
):
    spline_file_name = f"{image_id_string}_spline{spline_id:06d}.csv"
    spline_file_path = os.path.join(output_folder_path, spline_file_name)
    spline_data.to_csv(spline_file_path, index=False)


def _prepare_spline_data_for_saving(
    keypoints, fiber_diameter, image_width, image_height, x_min, y_min
):
    keypoints_x, keypoints_y = _separate_keypoint_coordinates(keypoints)
    keypoints_x, keypoints_y = _offset_keypoints(
        keypoints_x, keypoints_y, x_min, y_min
    )
    keypoints_y = _horizontally_mirror_keypoints(keypoints_y, image_height)
    spline_data = pd.DataFrame(
        {"x": keypoints_x, "y": keypoints_y, "width": fiber_diameter}
    )
    spline_data = _filter_keypoints_outside_of_image(
        spline_data, image_height, image_width
    )

    return spline_data


def _offset_keypoints(keypoints_x, keypoints_y, x_min, y_min):
    keypoints_x = [keypoint_x - x_min for keypoint_x in keypoints_x]
    keypoints_y = [keypoint_y - y_min for keypoint_y in keypoints_y]
    return keypoints_x, keypoints_y


def _separate_keypoint_coordinates(keypoints):
    keypoints_x = [keypoint[0] for keypoint in keypoints]
    keypoints_y = [keypoint[1] for keypoint in keypoints]
    return keypoints_x, keypoints_y


def _gather_spline_data(particles):
    keypoint_sets = blender.particles.get_hair_spline_keypoints(particles)
    fiber_diameters = blender.particles.get_hair_diameter(particles)
    return fiber_diameters, keypoint_sets


def _filter_keypoints_outside_of_image(spline_data, height, width):
    spline_data = spline_data.query(
        f"x>=0 and x<={width} and y>=0 and y<={height}"
    )
    return spline_data


def _horizontally_mirror_keypoints(keypoints_y, height):
    # flip y-axis (in blender the y-axis is oriented in the up-direction of the image)
    keypoints_y = [height - keypoint_y for keypoint_y in keypoints_y]
    return keypoints_y
