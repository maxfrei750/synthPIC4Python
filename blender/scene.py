import bpy
import os


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
        bpy.context.scene.cycles.samples = 32
    if engine == "BLENDER_EEVEE":
        bpy.context.scene.eevee.taa_render_samples = 32

    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.image_settings.color_depth = "8"
    bpy.context.scene.render.image_settings.compression = 0

    bpy.context.scene.render.film_transparent = True

    bpy.context.scene.use_gravity = False


def render_to_file(absolute_file_path):
    previous_path = bpy.context.scene.render.filepath
    bpy.context.scene.render.filepath = absolute_file_path
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.render.filepath = previous_path
