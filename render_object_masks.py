import bpy
import os

C = bpy.context
D = bpy.data
R = C.scene.render

image_id = 0

output_dir_base = "/tmp"

output_dir = os.path.join(output_dir_base, "object_masks")

previous_file_path = D.filepath
temp_file_path = previous_file_path + "_temp"

try:
    bpy.ops.wm.save_as_mainfile(filepath=temp_file_path)

    # Set render settings.
    R.image_settings.compression = 100
    R.image_settings.color_mode = "BW"
    R.use_compositing = False
    R.use_sequencer = False
    R.engine = "BLENDER_WORKBENCH"
    C.scene.display.shading.light = "FLAT"
    R.film_transparent = True
    C.scene.display.render_aa = "OFF"
    C.scene.display.shading.color_type = "SINGLE"
    C.scene.display.shading.single_color = (1, 1, 1)

    # Set black background.
    C.scene.world.use_nodes = False
    C.scene.world.color = (0, 0, 0)

    # Hide all meshes and replace their textures.
    for ob in D.objects:
        if ob.type == "MESH":
            ob.hide_render = True

    # Unhide meshes one by one and render them.
    mask_id = 0
    for ob in D.objects:
        if ob.type == "MESH":
            ob.hide_render = False

            output_filename = "image{:06d}_mask{:06d}.png".format(image_id, mask_id)
            output_path = os.path.join(output_dir, output_filename)
            R.filepath = output_path

            bpy.ops.render.render(write_still=True)

            ob.hide_render = True

            mask_id += 1

finally:
    bpy.ops.wm.open_mainfile(filepath=previous_file_path)
    os.remove(temp_file_path)
