import bpy
import numpy as np
import pymesh as pm


#Define vertices, faces, edges

# verts = np.array([[0,0,0],[0,5,0],[5,5,0],[5,0,0],[2.5,2.5,4.5]])*100
# faces = np.array([[0,1,2,3], [0,4,1], [1,4,2], [2,4,3], [3,4,0]])

mesh_raw = pm.generate_icosphere(200, np.array([0,0,0]), refinement_order=1)

verts = mesh_raw.vertices
faces = mesh_raw.faces

# Convert numpy arrays to lists.
verts = verts.tolist()
faces = faces.tolist()
 
#Define mesh and object
mesh = bpy.data.meshes.new("Particle")
object = bpy.data.objects.new("Particle", mesh)
 
#Set location and scene of object
object.location = bpy.context.scene.cursor_location
bpy.context.scene.objects.link(object)
 
#Create mesh
mesh.from_pydata(verts,[],faces)
mesh.update(calc_edges=True)


bpy.ops.render.render(write_still=True)