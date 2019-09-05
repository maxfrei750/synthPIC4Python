#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pymesh as pm

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import matplotlib.pyplot as plt


# In[2]:


A = pm.generate_icosphere(10,np.array([0,0,0]),refinement_order=3)


# In[3]:


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x = A.vertices[:,0]
y = A.vertices[:,1]
z = A.vertices[:,2]

print(y.shape)

# Plot the surface
ax.plot_trisurf(x, y, z, color='b')

plt.show()


# In[ ]:




