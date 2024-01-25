from __future__ import print_function
from __future__ import division
import cv2 as cv
import numpy as np
from sklearn.cluster import KMeans

n_colors = 3
preview_size = 300

src = cv.imread(cv.samples.findFile("images/11_2_1x_X10.jpeg"))

# image = cv.cvtColor(src, cv.COLOR_BGR2HSV)
image = src
# reshape the image to be a list of pixels
image = src.reshape((image.shape[0] * image.shape[1], 3))
clusters = KMeans(n_clusters=n_colors)
clusters.fit_predict(image)
colors = np.array([clusters.cluster_centers_], dtype=np.uint8)
# colors = cv.cvtColor(colors, cv.COLOR_HSV2BGR)
colors_image = np.zeros((preview_size, preview_size * n_colors, 3), dtype=np.uint8)
for i in range(n_colors):
    cv.rectangle(
        colors_image,
        (i * preview_size, 0),
        ((i + 1) * preview_size, preview_size),
        tuple(colors[0, i].tolist()),
        cv.FILLED,
    )
cv.imshow("colors", colors_image)
cv.waitKey(0)
