import pymesh
import numpy as np

# Generate a mesh.
radius = 200
center  = np.array([0,0,0])
refinement_order = 5

primitiveMesh = pymesh.generate_icosphere(radius, center, refinement_order=refinement_order)
primitiveMesh.add_attribute("vertex_normal");

vertexOffsets = np.random.randn(primitiveMesh.num_vertices,3) * primitiveMesh.get_vertex_attribute("vertex_normal")

deformedVertices = primitiveMesh.vertices + vertexOffsets
deformedFaces = primitiveMesh.faces
deformedMesh = pymesh.form_mesh(deformedVertices, deformedFaces)

# Save the mesh 
pymesh.save_mesh("./meshes/0001.ply", deformedMesh, *deformedMesh.get_attribute_names())