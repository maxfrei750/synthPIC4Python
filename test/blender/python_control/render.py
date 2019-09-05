import bpy

# Read input file.
bpy.ops.import_mesh.ply(filepath="./meshes/0001.ply")
 
# # #Set location and scene of object
# # object.location = bpy.context.scene.cursor_location
# # bpy.context.scene.objects.link(object)

# obj_object = bpy.context.selected_objects[0] ####<--Fix

bpy.ops.render.render(write_still=True)