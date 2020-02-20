import os
import random

import blender.utilities
import bpy
import numpy as np
import trimesh


def is_iterable(obj):
    try:
        _ = iter(obj)
    except TypeError:
        return False
    else:
        return True


def ensure_iterability(obj):
    if not is_iterable(obj):
        obj = [obj]

    return obj


def ensure_double_iterability(obj):
    if not is_iterable(obj):
        return [[obj]]
    elif not is_iterable(obj[0]):
        return [obj]


def select_only(particles):
    particles = ensure_iterability(particles)

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = particles[0]

    for particle in particles:
        particle.select_set(True)


def create_raw_dummy_mesh():
    mesh_raw = trimesh.creation.icosphere(subdivisions=5, radius=50)

    np.random.seed(1)
    deformation_strength = 0.5
    n_vertices = len(mesh_raw.vertices)
    vertex_offsets = (
        mesh_raw.vertex_normals
        * np.random.randn(n_vertices, 1)
        * deformation_strength
    )
    mesh_raw.vertices += vertex_offsets

    return mesh_raw


def hide(particles, state=True):
    particles = ensure_iterability(particles)

    for particle in particles:
        particle.hide_viewport = state
        particle.hide_render = state


def show(particles, state=True):
    hide(particles, state=(not state))


def load_primitive(blend_file):
    blend_file = os.path.abspath(blend_file)

    assert os.path.isfile(blend_file), "Could not find file: " + blend_file

    section = "\\Object\\"
    blender_object = "primitive"

    filepath = blend_file + section + blender_object
    directory = blend_file + section
    filename = blender_object

    bpy.ops.wm.append(
        filepath=filepath, filename=filename, directory=directory
    )

    primitive = bpy.data.objects[-1]

    return primitive


def duplicate(particle, new_name):
    new_particle = particle.copy()
    new_particle.data = particle.data.copy()
    new_particle.animation_data_clear()
    new_particle.name = new_name

    for i, particle_system in enumerate(particle.particle_systems):
        new_particle.particle_systems[
            i
        ].settings = particle_system.settings.copy()

    bpy.data.scenes["Scene"].collection.objects.link(new_particle)

    return new_particle


def delete(particles):
    particles = ensure_iterability(particles)

    bpy.ops.object.delete({"selected_objects": particles})
    blender.utilities.purge_unused_data()


def randomize_shape(particles):
    particles = ensure_iterability(particles)

    for particle in particles:
        if is_hair(particle):
            particle.particle_systems[0].seed = random.randint(0, 2147483647)
            particle.particle_systems[0].child_seed = random.randint(
                0, 2147483647
            )
        else:
            previous_location = tuple(particle.location)

            range_limit = 1e10

            x = random.randint(0, range_limit)
            y = random.randint(0, range_limit)
            z = random.randint(0, range_limit)

            # Move particle to randomize global noises.
            particle.location = (x, y, z)
            select_only(particle)
            bpy.context.view_layer.objects.active = particle
            bpy.ops.object.convert(target="MESH")

            # Reset location.
            particle.location = previous_location


def is_hair(particle):
    if (
        not particle.particle_systems
    ):  # Check if the particle has a blender particle system associated with it.
        return False
    else:  # If yes, then check whether it is of type hair.
        return particle.particle_systems[0].settings.type == "HAIR"


def get_hair_spline_vertices(particles):
    particles = ensure_iterability(particles)

    vertices_sets = []

    for particle in particles:

        assert is_hair(particle), "Expected particle to be a hair object."

        select_only(particle)

        modifier_name = particle.particle_systems[0].name

        # TODO: Replace the conversion of the modifier to a mesh with a data, instead of an operation based approach.
        bpy.ops.object.modifier_convert(modifier=modifier_name)

        temp_object = bpy.context.view_layer.objects.active
        temp_mesh = temp_object.data

        keypoints = []

        for vertex in temp_mesh.vertices:
            keypoints.append([vertex.co.x, vertex.co.y, vertex.co.z])

        vertices_sets.append(keypoints)

        delete(temp_object)

    return vertices_sets


def get_hair_spline_keypoints(particles):
    vertices_sets = get_hair_spline_vertices(particles)

    keypoint_sets = [
        [vertex[:2] for vertex in vertices] for vertices in vertices_sets
    ]

    return keypoint_sets


def set_hair_diameter(particles, root_diameter, tip_diameter=None):
    particles = ensure_iterability(particles)

    if tip_diameter is None:
        tip_diameter = root_diameter

    for particle in particles:
        assert is_hair(
            particle
        ), "Please use the set_size method for the sizing of non-hair objects."

        # Due to a bug in Blender (https://developer.blender.org/T73620),
        # the "radius" properties of hair systems are actually controlling the diameter.
        # This will be fixed by renaming the properties in Blender 2.82.
        particle.particle_systems[0].settings.radius_scale = 1
        particle.particle_systems[0].settings.root_radius = root_diameter
        particle.particle_systems[0].settings.tip_radius = tip_diameter


def get_hair_diameter(particles):
    particles = ensure_iterability(particles)

    diameters = []

    for particle in particles:
        assert is_hair(
            particle
        ), "Please use the set_size method for the sizing of non-hair objects."

        # Due to a bug in Blender (https://developer.blender.org/T73620),
        # the "radius" properties of hair systems are actually controlling the diameter.
        # This will be fixed by renaming the properties in Blender 2.82.
        diameter = (
            (
                particle.particle_systems[0].settings.root_radius
                + particle.particle_systems[0].settings.tip_radius
            )
            / 2
            * particle.particle_systems[0].settings.radius_scale
        )

        diameters.append(diameter)

    return diameters


def set_random_hair_length_factor(particles):
    particles = ensure_iterability(particles)

    for particle in particles:
        assert is_hair(
            particle
        ), "Please use the set_size method for the sizing of non-hair objects."

        particle.particle_systems[0].settings.child_length = random.random()


def set_hair_length_factor(particles, length_factor):
    particles = ensure_iterability(particles)

    for particle in particles:
        assert is_hair(
            particle
        ), "Please use the set_size method for the sizing of non-hair objects."

        particle.particle_systems[0].settings.child_length = length_factor


def set_size(particles, target_size_xyz):
    particles = ensure_iterability(particles)

    if not is_iterable(target_size_xyz):
        target_size_xyz = (target_size_xyz, target_size_xyz, target_size_xyz)

    for particle in particles:
        assert not is_hair(
            particle
        ), "Please use the set_hair_diameter and set_hair_length_factor methods for the sizing of hair objects."

        scale_xyz = tuple(
            a / b for a, b in zip(target_size_xyz, particle.dimensions)
        )
        particle.scale = scale_xyz


def get_size(particles):
    particles = ensure_iterability(particles)

    sizes = []

    for particle in particles:
        assert not is_hair(
            particle
        ), "Please use the get_mean_hair_diameter method for getting the sizes of hair objects."

        sizes.append(particle.scale)

    return sizes


def set_smooth_shading(particles, state):
    particles = ensure_iterability(particles)

    for particle in particles:
        for polygon in particle.data.polygons:
            polygon.use_smooth = state


def make_rigid(particles, state=True):
    if bpy.data.scenes["Scene"].rigidbody_world is None:
        bpy.ops.rigidbody.world_add()

    particles = ensure_iterability(particles)

    for particle in particles:
        if state:
            bpy.data.scenes["Scene"].rigidbody_world.collection.objects.link(
                particle
            )
        else:
            bpy.data.scenes["Scene"].rigidbody_world.collection.objects.unlink(
                particle
            )


def relax_collisions(particles, damping, collision_shape, n_frames):
    particles = ensure_iterability(particles)

    collision_shape = collision_shape.upper()
    bpy.data.scenes["Scene"].use_gravity = False

    if bpy.data.scenes["Scene"].rigidbody_world is None:
        bpy.ops.rigidbody.world_add()

    bpy.context.scene.rigidbody_world.enabled = True

    make_rigid(particles)

    for particle in particles:
        particle.rigid_body.collision_shape = collision_shape
        particle.rigid_body.angular_damping = damping
        particle.rigid_body.linear_damping = damping

    bpy.data.scenes["Scene"].frame_end = n_frames
    bpy.data.scenes["Scene"].rigidbody_world.point_cache.frame_end = n_frames
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all(bake=True)
    bpy.data.scenes["Scene"].frame_set(n_frames)


def place_randomly(
    particles,
    lower_space_boundaries_xyz,
    upper_space_boundaries_xyz,
    do_random_rotation=False,
):
    particles = ensure_iterability(particles)

    for particle in particles:
        random_location = tuple(
            np.random.randint(
                low=lower_space_boundaries_xyz, high=upper_space_boundaries_xyz
            )
        )
        particle.location = random_location

    if do_random_rotation:
        rotate_randomly(particles)


def place(particles, positions):
    particles = ensure_iterability(particles)
    positions = ensure_double_iterability(positions)

    for particle, position in zip(particles, positions):
        particle.location = tuple(position)


def rotate_randomly(particles):
    particles = ensure_iterability(particles)

    for particle in particles:
        random_rotation = tuple(np.random.rand(3) * 2 * np.pi)
        particle.rotation_euler = random_rotation


def generate_lognormal_fraction(
    primitive, name, n, d_g, sigma_g, particle_class="particle"
):
    hide(primitive, False)

    particles = list()

    mu_particle_size = np.log(d_g)
    sigma_particle_size = np.log(sigma_g)

    for particle_id in range(n):
        particle_name = name + "{:06d}".format(particle_id)
        particle = duplicate(primitive, particle_name)
        particle["class"] = particle_class

        randomize_shape(particle)

        size = np.random.lognormal(
            mean=mu_particle_size, sigma=sigma_particle_size
        )
        set_size(particle, size)

        particles.append(particle)

    hide(primitive)

    return particles
