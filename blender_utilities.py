import trimesh
import numpy as np
import bpy
import random


def create_raw_mesh():
    mesh_raw = trimesh.creation.icosphere(subdivisions=5, radius=50)

    np.random.seed(1)
    deformation_strength = 0.5
    n_vertices = len(mesh_raw.vertices)
    vertex_offsets = mesh_raw.vertex_normals * np.random.randn(n_vertices, 1) * deformation_strength
    mesh_raw.vertices += vertex_offsets

    return mesh_raw


def set_background_color(color):
    if len(color) == 3:
        color += (1,)

    world = bpy.data.worlds["World"]
    world.use_nodes = True

    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = color
    bg.inputs[1].default_value = 1.0


def append_primitive(blend_file):
    # blend_file = "D:/path/to/the/repository.blend"
    section = "\\Object\\"
    blender_object = "primitive"

    filepath = blend_file + section + blender_object
    directory = blend_file + section
    filename = blender_object

    bpy.ops.wm.append(
        filepath=filepath,
        filename=filename,
        directory=directory)

    primitive = bpy.data.objects[-1]

    return primitive


def duplicate_object(source_object, name):
    new_object = source_object.copy()
    new_object.data = new_object.data.copy()
    new_object.animation_data_clear()
    new_object.name = name
    bpy.context.scene.collection.objects.link(new_object)

    return new_object


def delete_objects(object_list):
    bpy.ops.object.delete({"selected_objects": [object_list]})


def randomize_and_bake_shape(particle):
    previous_location = tuple(particle.location)

    range_limit = 1000

    x = random.randint(0, range_limit)
    y = random.randint(0, range_limit)
    z = random.randint(0, range_limit)

    print((x, y, z))

    # Move particle to randomize global noises.
    particle.location = (x, y, z)

    # bpy.context.scene.objects.active = particle
    # bpy.context.view_layer.objects.active = particle
    bpy.ops.object.select_all(action="DESELECT")
    particle.select_set(True)
    bpy.context.view_layer.objects.active = particle
    bpy.ops.object.convert(target="MESH")

    # Reset location.
    particle.location = previous_location


def set_size(particle, target_size_xyz):
    # if len(target_size_xyz) == 1:
    #     target_size_xyz = (target_size_xyz, target_size_xyz, target_size_xyz)

    scale_xyz = tuple(a / b for a, b in zip(target_size_xyz, particle.dimensions))
    particle.scale = scale_xyz


def set_smooth_shading(particle, state):
    for polygon in particle.data.polygons:
        polygon.use_smooth = state


def make_rigid(obj, state):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)

    if state:
        bpy.ops.rigidbody.objects_add(type="ACTIVE")
    else:
        bpy.ops.rigidbody.objects_remove()


def relax_collisions(particle_list,
                     damping,
                     collision_shape,
                     n_frames):
    collision_shape = collision_shape.upper()
    bpy.context.scene.use_gravity = False

    if bpy.context.scene.rigidbody_world is None:
        bpy.ops.rigidbody.world_add()

    bpy.context.scene.rigidbody_world.enabled = True

    for particle in particle_list:
        make_rigid(particle, True)

        particle.rigid_body.collision_shape = collision_shape
        particle.rigid_body.angular_damping = damping
        particle.rigid_body.linear_damping = damping

    bpy.context.scene.frame_end = n_frames
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all(bake=True)
    bpy.context.scene.frame_set(n_frames)


def place_randomly(particle_list,
                   lower_space_boundaries_xyz,
                   upper_space_boundaries_xyz,
                   do_random_rotation=False):
    for particle in particle_list:
        random_location = tuple(np.random.randint(low=lower_space_boundaries_xyz,
                                                  high=upper_space_boundaries_xyz))
        particle.location = random_location

        if do_random_rotation:
            random_rotation = tuple(np.random.rand(3) * 2 * np.pi)
            particle.rotation_euler = random_rotation


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
        print(device)
        device.use = True


def apply_default_settings():
    bpy.context.scene.render.engine = "CYCLES"
    enable_all_rendering_devices()
    bpy.context.scene.cycles.samples = 64

    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.image_settings.color_depth = "8"
    bpy.context.scene.render.image_settings.compression = 0

    bpy.context.scene.render.film_transparent = True

    bpy.context.scene.use_gravity = False
