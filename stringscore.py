#!/usr/bin/env python
# coding: utf-8

# In[11]:


# import cv2
import math
import numpy as np
from PIL import Image
import scipy
import scipy.misc
import scipy.sparse
import scipy.sparse.linalg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from artboard import Artboard, Yarn
N_PINS=200
N_STRINGS = 1000
DIAMETER=304.8
DIMENSION = 500
FADE = 25
FILE = 'img/wolf.jpg'
board = Artboard(DIAMETER, N_PINS)

#random 500x500 image
img = np.array(Image.open(FILE))
if img.ndim > 2:
    img = img[:, :, 0] #flatten to 1 channel - in prod, will need to loop over all channels
plt.imshow(img, cmap="gray")
plt.colorbar()


# In[12]:


board.setup_image(img)


# In[13]:


board.generate_stringscape(N_STRINGS, 25, 25)


# In[14]:


board.render(background="white").rasterize()


# In[16]:


plt.imshow(img, cmap="gray")

