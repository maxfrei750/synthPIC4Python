import bpy
import os
from utilities import get_random_string
import blender.particles


class TemporaryState:
    def __init__(self):
        self.original_path = bpy.data.filepath
        self.temporary_path = self.original_path + "_state_"+get_random_string()

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
        bpy.context.scene.cycles.samples = 16
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


def render_object_masks(particles, image_id_string, absolute_output_directory):
    particles = blender.particles.ensure_iterability(particles)

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

            output_filename = image_id_string + "_mask{:06d}.png".format(mask_id)
            output_file_path = os.path.join(absolute_output_directory, output_filename)
            render_to_file(output_file_path)

            blender.particles.hide(particle)


def create_diffuse_color_material(name, color):
    material = (bpy.data.materials.get(name) or bpy.data.materials.new(name))
    material.diffuse_color = color
    return material


def replace_material(instance, material):
    instance.data.materials.clear()
    instance.data.materials.append(material)


def render_occlusion_masks(particles, image_id_string, absolute_output_directory):
    particles = blender.particles.ensure_iterability(particles)

    with TemporaryState():
        # Set render settings.
        setup_workbench_renderer()
        bpy.context.scene.display.shading.color_type = "MATERIAL"

        material_white = create_diffuse_color_material("white_mask_material", (1, 1, 1, 1))
        material_black = create_diffuse_color_material("black_mask_material", (0, 0, 0, 1))

        # Replace textures of all meshes with black texture.
        for instance in bpy.data.objects:
            if instance.type == "MESH":
                replace_material(instance, material_black)

        # Change texture of particles to white texture one by one and render them.
        for mask_id, particle in enumerate(particles):
            replace_material(particle, material_white)

            output_filename = image_id_string + "_mask{:06d}.png".format(mask_id)
            output_file_path = os.path.join(absolute_output_directory, output_filename)
            render_to_file(output_file_path)

            replace_material(particle, material_black)
