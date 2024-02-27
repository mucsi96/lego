from __future__ import print_function
from __future__ import division
import cv2 as cv
from matplotlib import pyplot
import numpy as np
from sklearn.cluster import KMeans

n_colors = 6
preview_size = 300

src = cv.imread(cv.samples.findFile("images/11_2_1x_X9.jpeg"))

# image = cv.cvtColor(src, cv.COLOR_BGR2HSV)
image = src
image = src.reshape((-1, 3))
image = np.float32(image)
clusters = KMeans(n_clusters=n_colors, random_state=0)
labels = clusters.fit_predict(image)
bincount = np.bincount(labels)
colors = clusters.cluster_centers_.astype(np.uint8)
rgba_colors = [(color[2] / 255.0, color[1] / 255.0, color[0] / 255.0, 1) for color in colors]

sorted_indices = sorted(range(len(bincount)), key=lambda k: bincount[k], reverse=True)
sorted_labels = [bincount[i] for i in sorted_indices]
sorted_colors = [rgba_colors[i] for i in sorted_indices]

pyplot.pie(sorted_labels, None, None, sorted_colors)
pyplot.show()