import trimesh
import numpy as np
import bpy
import random
from ..utilities import is_iterable


def create_raw_dummy_mesh():
    mesh_raw = trimesh.creation.icosphere(subdivisions=5, radius=50)

    np.random.seed(1)
    deformation_strength = 0.5
    n_vertices = len(mesh_raw.vertices)
    vertex_offsets = mesh_raw.vertex_normals * np.random.randn(n_vertices, 1) * deformation_strength
    mesh_raw.vertices += vertex_offsets

    return mesh_raw


def load_primitive(blend_file):
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


def duplicate(particle, new_name):
    new_particle = particle.copy()
    new_particle.data = new_particle.data.copy()
    new_particle.animation_data_clear()
    new_particle.name = new_name
    bpy.context.scene.collection.objects.link(new_particle)

    return new_particle


def delete(particles):
    bpy.ops.object.delete({"selected_objects": [particles]})


def randomize_and_bake_shape(particles):
    if not is_iterable(particles):
        particles = list(particles)

    for particle in particles:
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


def set_size(particles, target_size_xyz):
    if not is_iterable(particles):
        particles = list(particles)

    for particle in particles:
        scale_xyz = tuple(a / b for a, b in zip(target_size_xyz, particle.dimensions))
        particle.scale = scale_xyz


def set_smooth_shading(particles, state):
    if not is_iterable(particles):
        particles = list(particles)

    for particle in particles:
        for polygon in particle.data.polygons:
            polygon.use_smooth = state


def make_rigid(particles, state):
    if not is_iterable(particles):
        particles = list(particles)

    for particle in particles:
        bpy.ops.object.select_all(action="DESELECT")
        particle.select_set(True)

        if state:
            bpy.ops.rigidbody.objects_add(type="ACTIVE")
        else:
            bpy.ops.rigidbody.objects_remove()


def relax_collisions(particles,
                     damping,
                     collision_shape,
                     n_frames):
    collision_shape = collision_shape.upper()
    bpy.context.scene.use_gravity = False

    if bpy.context.scene.rigidbody_world is None:
        bpy.ops.rigidbody.world_add()

    bpy.context.scene.rigidbody_world.enabled = True

    for particle in particles:
        make_rigid(particle, True)

        particle.rigid_body.collision_shape = collision_shape
        particle.rigid_body.angular_damping = damping
        particle.rigid_body.linear_damping = damping

    bpy.context.scene.frame_end = n_frames
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all(bake=True)
    bpy.context.scene.frame_set(n_frames)


def place_randomly(particles,
                   lower_space_boundaries_xyz,
                   upper_space_boundaries_xyz,
                   do_random_rotation=False):
    for particle in particles:
        random_location = tuple(np.random.randint(low=lower_space_boundaries_xyz,
                                                  high=upper_space_boundaries_xyz))
        particle.location = random_location

        if do_random_rotation:
            random_rotation = tuple(np.random.rand(3) * 2 * np.pi)
            particle.rotation_euler = random_rotation
