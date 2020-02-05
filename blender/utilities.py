import bpy


def purge_unused_data():
    for data in bpy.data.meshes:
        if not data.users:
            bpy.data.meshes.remove(data)

    for data in bpy.data.materials:
        if not data.users:
            bpy.data.materials.remove(data)

    for data in bpy.data.textures:
        if not data.users:
            bpy.data.textures.remove(data)

    for data in bpy.data.images:
        if not data.users:
            bpy.data.images.remove(data)
