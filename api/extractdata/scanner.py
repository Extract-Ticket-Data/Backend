import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import os

def rectify(h):
  h = h.reshape((4,2))
  hnew = np.zeros((4,2),dtype = np.float32)

  add = h.sum(1)
  hnew[0] = h[np.argmin(add)]
  hnew[2] = h[np.argmax(add)]

  diff = np.diff(h,axis = 1)
  hnew[1] = h[np.argmin(diff)]
  hnew[3] = h[np.argmax(diff)]

  return hnew

def auto_crop(imag, path):
  v = np.median(imag)
  sigma = 0.33
  lower = int(max(0, (1.0 - sigma) * v))
  upper = int(min(255, (1.0 + sigma) * v))
  edged = cv2.Canny(imag,lower,upper)
  orig_edged = edged.copy()
  mpimg.imsave(path+'_edged.jpg',edged, cmap = plt.get_cmap('gray'))
  edged = cv2.imread(path+'_edged.jpg',0)
  os.remove(path+'_edged.jpg')

  (contours, _) = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
  contours = sorted(contours, key=cv2.contourArea, reverse=True)

  for err_relax in [0.02,0.03,0.04,0.05,0.06,0.1]:
    flag = 0
    # get approximate contour
    img_area = imag.shape[0] * imag.shape[1]
    for c in contours:
      area = cv2.contourArea(c)
      if area > (img_area/3):
        epsilon = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, err_relax * epsilon, True)
        if len(approx) == 4:
          print('contour found...')
          flag = 1
          target = approx
          break
    if flag == 1:
      break


  try:
    approx = rectify(target)
    x = imag.shape[1]
    y = imag.shape[0]
    pts2 = np.float32([[0,0],[x,0],[x,y],[0,y]])

    M = cv2.getPerspectiveTransform(approx,pts2)
    dst = cv2.warpPerspective(imag,M,(x,y))

    cv2.drawContours(imag, [target], -1, (0, 255, 0), 2)
    dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

  except:
    dst = imag


  return orig_edged, dst

def show_auto_crop_results(orig,orig_edged,image,dst):
  fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2,figsize=(12,12))
  ax1.imshow(orig)
  ax2.imshow(orig_edged,cmap='Greys_r')
  ax3.imshow(image)
  ax4.imshow(dst,cmap='Greys_r')
  ax1.set_title('Original')
  ax2.set_title('Edged')
  ax3.set_title('Contour')
  ax4.set_title('Presceptive')

def image_clear(I):
  try:
    I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
  except:
    print("",end='')
  try:
    I = np.uint8(I)
  except:
    print("",end='')
  size = min(151, (2*(min(I.shape[0],I.shape[1])//3) + 1))
  F = cv2.GaussianBlur(I,(size,size),0)
  #F = cv2.medianBlur(I,size)
  P = I * np.mean(F)
  C = I.copy()
  for col in range(P.shape[0]):
    for row in range(P.shape[1]):
      try :
        C[col,row] = P[col,row]/F[col,row]
      except :
        C[col,row] = P[col,row]
  H = cv2.adaptiveThreshold(C,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
  for i in range(H.shape[0]):
    for j in range(H.shape[1]):
      if C[i,j]<50:
        H[i,j]=0
      elif C[i,j]>200:
        H[i,j]=1
  H = cv2.medianBlur(H,7) # to remove paper salt noise
  return F,C,H

def show_final_clear_image_results(img, res):
  fig, ((ax1, ax2)) = plt.subplots(1, 2,figsize=(12,12))
  ax1.imshow(img,cmap='Greys_r')
  ax2.imshow(res,cmap='Greys_r')
  ax1.set_title('Original')
  ax2.set_title('Cleared')


def Main(path):
  imag = cv2.imread(path)
  orig = imag.copy()
  orig_edged, dst = auto_crop(imag, path)
  show_auto_crop_results(orig,orig_edged,imag,dst)
  I = dst.copy()
  blur_image, filtered_image, cleared_image = image_clear(I)
  I = imag.copy()
  blur_image_orig, filtered_image_orig, cleared_image_orig = image_clear(I)
  show_final_clear_image_results(I,cleared_image)
  mpimg.imsave(path+'1.jpg', cleared_image, cmap = plt.get_cmap('gray'))
  mpimg.imsave(path+'2.jpg', filtered_image, cmap = plt.get_cmap('gray'))
  mpimg.imsave(path+'3.jpg', filtered_image_orig, cmap = plt.get_cmap('gray'))
  #return cleared_image, filtered_image, filtered_image_orig