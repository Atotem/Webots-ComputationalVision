#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
from skimage.transform import hough_line, hough_line_peaks
from matplotlib import cm

img = cv2.imread('img/captura2.PNG')
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


plt.title('Blue Cube Channels Histogram')
R_hst = cv2.calcHist([img_rgb], [0], None, [256], [0, 255])
G_hst = cv2.calcHist([img_rgb], [1], None, [256], [0, 255])
B_hst = cv2.calcHist([img_rgb], [2], None, [256], [0, 255])
plt.plot(R_hst, c='red', label='R Channel')
plt.plot(G_hst, c='green', label='G Channel')
plt.plot(B_hst, c='blue', label='B Channel')
plt.ylabel('frecuency')
plt.xlabel('intensity')
plt.legend()
plt.show()
# %%
plt.imshow(img_rgb[30:50, 40:100])
plt.show()
# %%

sect = img_rgb[30:50, 40:100]
B_hst = cv2.calcHist([sect], [2], None, [256], [0, 255])
plt.plot(B_hst, c='blue')
plt.show()

# %%
plt.imshow(img_rgb)
plt.show()
# %%
# threshold: select range of color blue (~207)
img_proc = np.where((img_rgb[:, :, 2] > 205) & (img_rgb[:, :, 2] < 220), img_rgb[:, :, 2], 0)

plt.imshow(img_proc, cmap='gray')
plt.show()
# %%
# border of object
R = cv2.Canny(img_proc, threshold1=205, threshold2=220)

plt.imshow(R, cmap='gray')
plt.show()
# %%
# hough lines
angulos = np.linspace(-np.pi/2, np.pi/2, 360)
h, theta, d = hough_line(R, theta=angulos)

# Mapa de acumulación
fig = plt.figure(figsize=(10, 10))
plt.subplot(111)
plt.imshow(np.log(1 + h),
             extent=[np.rad2deg(theta[-1]), np.rad2deg(theta[0]), d[-1], d[0]],
             cmap=cm.hot,aspect=1/15)

# %%
valores_maximos= hough_line_peaks(h, theta, d)
print(valores_maximos)
# %%
img_proc[20:40, 20:40] # 0 or original values
# %%
R[20:40, 20:40] # 0 or 255
# %%
# ret, thresh1 = cv2.threshold(img_proc, 120, 255, cv2.THRESH_BINARY)
# ret, thresh2 = cv2.threshold(R, 120, 255, cv2.THRESH_BINARY)
#%%
img_crcl = cv2.imread('img/captura3.png')
img_crcl_rgb = cv2.cvtColor(img_crcl, cv2.COLOR_BGR2RGB)

plt.imshow(img_crcl_rgb)
plt.show()
# %%
# threshold: select range of color red (~207)
img_crcl_proc = np.where((img_crcl_rgb[:, :, 0] > 205) & (img_crcl_rgb[:, :, 0] < 230), img_crcl_rgb[:, :, 0], 0)

C = cv2.Canny(img_crcl_proc, threshold1=205, threshold2=230)

plt.imshow(C, cmap='gray')
plt.show()
# %%
# hough lines
angulos = np.linspace(-np.pi/2, np.pi/2, 360)
h, theta, d = hough_line(C, theta=angulos)

# Mapa de acumulación
fig = plt.figure(figsize=(10, 10))
plt.subplot(111)
plt.imshow(np.log(1 + h),
             extent=[np.rad2deg(theta[-1]), np.rad2deg(theta[0]), d[-1], d[0]],
             cmap=cm.hot,aspect=1/15)
# %%
valores_maximos= hough_line_peaks(h, theta, d)
print(len(valores_maximos[0]))

# %%
from skimage import measure

ret, thresh1 = cv2.threshold(img_proc, 120, 255, cv2.THRESH_BINARY)
# ret, thresh2 = cv2.threshold(R, 120, 255, cv2.THRESH_BINARY)
# ret, thresh3 = cv2.threshold(img_crcl_proc, 120, 255, cv2.THRESH_BINARY)
# ret, thresh4 = cv2.threshold(C, 120, 255, cv2.THRESH_BINARY)

all_labels = measure.label(thresh1)
region = measure.regionprops(label_image=all_labels)
# %%
print(region[0].centroid)
print(region[0].bbox) # x1 y1 x2 y2

# %%
plt.imshow(thresh1)
plt.show()
# %%
coord = [[957.114, 880.314, 803.514], [36, 40, 42]]

plt.plot(coord[0], coord[1])
plt.show()
# %%
coef = np.polyfit(coord[0], coord[1], 1)
fn = np.poly1d(coef)

plt.title('Sensor Distance vs Bounding Box Difference')
plt.plot(coord[0], coord[1], coord[0], fn(coord[0]), '--k')
plt.ylabel('column diff')
plt.xlabel('distance')
plt.show()
# %%
print(fn(1000.0))
# %%
coef = np.polyfit(coord[1], coord[0], 1)
fn = np.poly1d(coef)

coef = np.polyfit(coord[1], coord[0], 1)

print(fn(34.5))
# %%
ret, thresh3 = cv2.threshold(img_crcl_proc, 120, 255, cv2.THRESH_BINARY)

all_labels = measure.label(thresh3)
region = measure.regionprops(label_image=all_labels)
print(region[0].centroid)
print(region[0].bbox) # x1 y1 x2 y2

# %%
plt.imshow(thresh3)
plt.show()
# %%
print(np.any(np.array(region[0].bbox) > 63))
# %%
np.array(region[0].bbox)[0]
# %%
m,b = np.polyfit(coord[1], coord[0], 1)
print(m)
print(b)
# %%
print(38*m - b)
# %%
fn(39)
# %%
point = cv2.imread('img/captura4.png')
point_rgb = cv2.cvtColor(point, cv2.COLOR_BGR2RGB)

plt.imshow(point_rgb)
plt.show()
# %%
R_hst = cv2.calcHist([point_rgb], [0], None, [256], [0, 255])
G_hst = cv2.calcHist([point_rgb], [1], None, [256], [0, 255])
B_hst = cv2.calcHist([point_rgb], [2], None, [256], [0, 255])
# plt.plot(R_hst, c='red')
# plt.plot(G_hst, c='green')
plt.plot(B_hst, c='blue')
plt.show()
# %%
