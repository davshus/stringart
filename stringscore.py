#!/usr/bin/env python
# coding: utf-8

# In[5]:


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
N_PINS=500
N_STRINGS = 1500
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


# In[6]:


board.generate_stringscape(img, N_STRINGS, 25, 25)


# In[7]:


board.render(background="white").rasterize().savePng("build/export.png")


# In[8]:


plt.imshow(img, cmap="gray")
plt.show()
