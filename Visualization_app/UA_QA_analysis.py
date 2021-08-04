# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 15:31:51 2020

@author: sinkinen
"""

#import matplotlib.pyplot as plt
import pydicom
import numpy as np
from os import listdir
from os.path import isfile, join
from skimage.measure import label   
import cv2 as cv
from scipy.signal import argrelextrema
from scipy import ndimage
import cv2
#import matplotlib as mpl
#mpl.rcParams['figure.dpi']= 150



def getLargestCC(segmentation):
    '''
    Parameters
    ----------
    segmentation: binary image 

    Returns
    -------
    largestCC: Largest connected component 

    '''
    labels = label(segmentation)
    largestCC = labels == np.argmax(np.bincount(labels.flat))
    return largestCC


def fillhole(input_image):
    '''
    input gray binary image  get the filled image by floodfill method
    Note: only holes surrounded in the connected regions will be filled.
    :param input_image: binary image
    :return: filled image
    '''
    im_flood_fill = input_image.copy()
    h, w = input_image.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    im_flood_fill = im_flood_fill.astype("uint8")
    cv.floodFill(im_flood_fill, mask, (0, 0), 255)
    im_flood_fill_inv = cv.bitwise_not(im_flood_fill)
    img_out = input_image | im_flood_fill_inv
    return img_out 


def rgb2gray(rgb):
    '''
    Parameters
    ----------
    rgb : RGB - image

    Returns
    -------
    gray : Grayscale image

    '''
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray    



def crop_US_im(im, crop2half=True):
    '''
    Parameters
    ----------
    crop2half: flag for additional half row crop
    im : Ultrasound image in RGB or grayscale

    Returns
    -------
    im_crop : Cropped image to analysis content

    '''
    
    if len(im.shape) == 3: #Change to grayscale  
        im = rgb2gray(im)
        
    #-- Pre-process --        
    BW = im > 0 #Threshold image    
    label_im, nb_labels = ndimage.label(BW)
    sizes = ndimage.sum(BW, label_im, range(nb_labels + 1))
    loc = np.argmax(sizes)
    BW = label_im==loc
    L = BW.astype(float)   
    
    # Crop row:
    vals = np.argwhere(L==1)    
    x = vals[:,0]
    
    x_min = np.min(x)
    x_max = np.max(x)
    im_crop = im[x_min:x_max,:]    
    
    #Crop column:
    BW = im_crop[0:100,:] > 0 #take first 100 rows to avoid the colorbar 
    L = BW.astype(float)   
    vals = np.argwhere(L==1)    
    y = vals[:,1]
    
    y_min = np.min(y)
    y_max = np.max(y)
    
    im_crop = im_crop [:,y_min:y_max]    


    if crop2half==True:
            #Vertical crop to half: 
            x = np.round(im_crop.shape[0]/2)
            im_crop = im_crop[0 : x.astype(int), :] 
     
    return im_crop

    
def smooth(y, box_pts):
    '''
    smooths vector y with box convolution length box_pts
    Parameters
    ----------
    y : vector profile
        
    box_pts : box vector length

    Returns
    -------
    y_smooth : smoothed vector

    '''

    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def get_reverb_lines(vert_profile, reverb_lines, smooth_factor = 5):
    '''
    returns reverberation line positions from detrended vertical profile minimas

    Parameters
    ----------
    vert_profile : vertical profile vector
    reverb_lines : scalar of how many lines are being detected
    smooth_factor : how much detrended profile will be smoothed 
         The default is 5.

    Returns
    -------
    XX : vector of reverb line locations

    '''

    detrend = np.zeros(vert_profile.shape)
    vert_profile2 = smooth(vert_profile, smooth_factor)
    
    for t in range(1,vert_profile.shape[0]):
        detrend[t] = vert_profile2[t] - vert_profile2[t-1]
    
    detrend[0] = detrend[1]
    
    #plt.plot(detrend)
    #plt.show()
    
    locs = argrelextrema(detrend, np.less)
    locs= locs[0]
    XX = locs[0:reverb_lines] + smooth_factor
    
    return XX

def transform_convex_image2linear(im):
    '''
    This function transforms the convex transducer image to linear using 
    polar transform

    Parameters
    ----------
    im : convex image

    Returns
    -------
    polar_image : Polar image 

    '''

    #--Pre-crop --
    BW = im  > 0 #Threshold image    
    label_im, nb_labels = ndimage.label(BW)
    sizes = ndimage.sum(BW, label_im, range(nb_labels + 1))
    loc = np.argmax(sizes)
    BW = label_im==loc
        
    #corner locations:
    vals = np.argwhere(BW==1)
    
    x = vals[:,0]
    y = vals[:,1]    

    y_min = np.min(y)
    y_max = np.max(y)
    x_min = np.min(x)
    x_max = np.max(x)
    
    #Crop image to content:
    im_crop = im[x_min:x_max,y_min:y_max]
    
    #tight crop to edge fits:
    x = np.round(im_crop.shape[0]*0.5)
     
    BW = im_crop[ 0:x.astype(int) , :]  > 0 
    label_im, nb_labels = ndimage.label(BW)
    sizes = ndimage.sum(BW, label_im, range(nb_labels + 1))
    loc = np.argmax(sizes)
    BW = label_im == loc
    
    # Find edge pixels using for loop: 
    left_vals = np.zeros((90, 2))
    right_vals = np.zeros((90, 2))    
    count=0
    for  row in range(10, 100, 1):
        profile = BW[row,:]
        loc_l = np.argmax(profile)
        loc_r = np.argmax(np.flipud(profile))
        loc_r  = BW.shape[1]-loc_r
        
        left_vals[count,:] = [row, loc_l]
        right_vals[count,:] = [row, loc_r]
        count+=1
    
    ##sanity plot:
   # plt.imshow(BW)
   # plt.plot(left_vals[:,1], left_vals[:, 0])
   # plt.plot(right_vals[:,1], right_vals[:, 0])
   # plt.show()
    
    #Line fits:
    x_r = right_vals[:,1]
    y_r = right_vals[:,0]     
    m_r, b_r = np.polyfit(x_r, y_r, 1) 
    #m = slope, b = intercept.
    
    x_l = left_vals[:,1]
    y_l = left_vals[:,0]     
    m_l, b_l = np.polyfit(x_l, y_l, 1) 
    
    # intersection:
    x_int = (b_l-b_r)/(m_r-m_l)
    y_int = m_r*x_int+b_r
        
    ##sanity plot 2
  #  plt. plot(x_r, y_r, 'ko') 
  #  plt. plot(x_r, m_r*x_r + b_r) 
    #
  #  plt. plot(x_l, y_l, 'ro') 
  #  plt. plot(x_l, m_l*x_l + b_l) 
    #
  #  plt. plot(x_int, y_int, 'bo')
  #  plt.show()
    
    #take whole image:
    x = np.round(im_crop.shape[0]*1)
    
    BW = im_crop[ 0:x.astype(int) , :]  > 0 
    label_im, nb_labels = ndimage.label(BW)
    sizes = ndimage.sum(BW, label_im, range(nb_labels + 1))
    loc = np.argmax(sizes)
    BW = label_im == loc
    
    im_crop2 = im_crop[ 0:x.astype(int) , :]*BW
    
    offset = np.round(np.abs(y_int))
    offset = offset.astype(int)
    temp = np.zeros((im_crop2.shape[0]+offset, im_crop2.shape[1]))    
    temp[offset:,:] = im_crop2

    # enlanrge to cover whole area:
    temp_disk = np.zeros((2*temp.shape[0], 2*temp.shape[0])) 
    
    offset2 = np.round(temp_disk.shape[0]/2) 
    offset2 = offset2.astype(int)
    offset3 = np.round(-temp.shape[1]/2 + temp_disk.shape[1]/2) 
    offset3 = offset3.astype(int)
    end_loc3 = offset3+temp.shape[1]
    end_loc3 = end_loc3.astype(int)
 #   import pdb; pdb.set_trace()
    temp_disk[ offset2: ,  offset3:end_loc3 ] = temp
 
    #--- ensure image is of the type float ---
    img = temp_disk.astype(np.float32)
    
    #--- the following holds the square root of the sum of squares of the image dimensions ---
    #--- this is done so that the entire width/height of the original image is used to express the complete circular range of the resulting polar image ---
    value = np.sqrt(((img.shape[0]/2.0)**2.0)+((img.shape[1]/2.0)**2.0))
    
    polar_image = cv2.linearPolar(img,(img.shape[0]/2, img.shape[1]/2), value, cv2.WARP_FILL_OUTLIERS)
    
    polar_image = np.transpose(polar_image)
    polar_image = np.fliplr(polar_image)

    return polar_image

def US_air_image_analysis(im_crop, reverb_lines = 4 ):
    '''
    Ultrasound air image analysis on cropped image im_crop

    Parameters
    ----------
    im_crop : cropped input image

    reverb_lines : scalar how many reverb line will be detected
        The default is 4.

    Returns
    -------
    vert_profile : vector, vertical profile
        
    horizon_profile : vector, horizontal profile
        
    S_depth : scalar, pixel value depth 
        
    U_cov : scalar, horizontal profile covariance
        
    U_skew : scalar, horizontal profile skewness 
        
    U_low : list, horizontal profile segment 10%, 20%, 40%, 20%, 10%
            MSE minimum for each segment

    '''

    # --- Vertical profile ---
    vert_profile = np.median(im_crop, axis = 1)
    
    background = im_crop[np.round(im_crop.shape[0]/2).astype(int):,:]
    background_value = np.median(background.ravel())
    
    # S_depth:
    S_depth = np.argmin(np.abs(vert_profile-background_value))
    
    #plt.plot(vert_profile)
    #plt.plot([S_depth], [background_value], 'r.')
    #plt.show()
    
    # Horizontal profile:
    #Calculate the reverb lines positions:
    XX = get_reverb_lines(vert_profile, reverb_lines, smooth_factor = 5)
        
    horizon_profile = np.mean(im_crop[0:XX[-1],:], axis = 0)
    
    u = horizon_profile
    
    X_u = np.linspace(0, 100, len(horizon_profile))
    
    #plt.plot(X_u,horizon_profile)
    #plt.show()
    
    #Parameters:
    U_cov = 100*(np.std(u)/np.mean(u))
    m3 = (1/len(u))*np.sum((u-np.mean(u))**3)
    m32 = (1/len(u))*np.sum(np.abs((u-np.mean(u)))**(3/2))
    U_skew = m3/m32
    
    #Segments:
    segment = np.array([10, 20, 40, 20, 10])
    
    U_low = []
    ind_prev = 0
    seg = 0
    for s in range(len(segment)):
        seg  = seg + segment[s]
        ind = np.argmin(np.abs(X_u-seg))
        v = u[ind_prev:ind]
        
        U_low_val = 100*np.min((v-np.median(u))/np.median(u)) 
        U_low.append(np.abs(U_low_val))
 
        ind_prev = ind + 1 

    return vert_profile, horizon_profile, S_depth, U_cov, U_skew, U_low

class AirScanAnalysisRes():
    '''Class of to store results with getters and setters '''
    
    
    def __init__(self, name,transducer_name, unit, im, vert_profile, horiz_profile,
                 S_depth, U_cov, U_skew, U_low, reverb_lines):
        self.name = name
        self.transducer_name = transducer_name
        self.unit = unit
        self.im = im
        self.vert_profile = vert_profile
        self.horiz_profile = horiz_profile
        self.S_depth = S_depth
        self.U_cov = U_cov
        self.U_skew = U_skew
        self.U_low = U_low
        self.reverb_lines = reverb_lines 
    
    #getterit:        
    def get_name(self):
        return self.name
    def get_transducer_name(self):
        return self.transducer_name
    def get_unit(self):
        return self.unit
    def get_im(self):
        return self.im
    def get_vert_profiles(self):
        return self.vert_profile
    def get_horiz_profiles(self):
        return self.horiz_profile
    def get_S_depth(self):
        return self.S_depth
    def get_U_cov(self):
        return self.U_cov
    def get_U_skew(self):
        return self.U_skew
    def get_U_low(self):
        return self.U_low
    def get_reverb_lines(self):
        return self.reverb_lines
    #Setterit:
    def set_name(self, name):
        self.name=name
    def set_transducer_name(self, transducer_name):
        self.transducer_name=transducer_name
    def set_unit(self, unit):
        self.unit=unit
    def set_im(self, im):
        self.im = im
    def set_vert_profiles(self,vert_profile):
        self.vert_profile=vert_profile
    def set_horiz_profiles(self,horiz_profile):
        self.horiz_profile=horiz_profile
    def set_S_depth(self,S_depth):
        self.S_depth=S_depth
    def set_U_cov(self,U_cov):
        self.U_cov=U_cov
    def set_U_skew(self,U_skew):
        self.U_skew=U_skew
    def set_U_low(self,U_low):
        self.U_low=U_low
    def set_reverb_lines(self,reverb_lines):
        self.reverb_lines=reverb_lines        


def MAIN_US_analysis(path_data):
    '''
    Main function to perform air scan analysis on image defined on
    path path_data
    Parameters
    ----------
    path_data : str, path to data

    Returns
    -------
    res : AirScanAnalysisRes class object, contains results
        
    '''
    
    data = pydicom.dcmread(path_data)
       
    # --- Metadata ---  
    TransducerType = data.TransducerType
    Physical_Delta_X  = data.SequenceOfUltrasoundRegions[0]['0x0018602c'].value
    Physical_Delta_Y  = data.SequenceOfUltrasoundRegions[0]['0x0018602e'].value
    unit = data.SequenceOfUltrasoundRegions[0]['0x00186024'].value
    name = data[0x00081010].value
    transducer_name = data[0x00186031].value
    
    if unit == 3:
        unit ='cm'
    else: 
        unit = 'not in meters'
        
    #Obtain air scan image:        
    im = data.pixel_array
    im = rgb2gray(im)   
    
    if TransducerType == 'CURVED LINEAR': #convex
        im_t =  transform_convex_image2linear(im)  #transforms to linear
        im_crop = crop_US_im(im_t, crop2half=False)
        reverb_lines = 5
        
    else: #linear
        im_crop = crop_US_im(im, crop2half=True)
        reverb_lines = 4
       
    # --- Analysis ---
    vert_profile, horizon_profile, S_depth, U_cov, U_skew, U_low = US_air_image_analysis(im_crop, reverb_lines )
    
    S_depth = S_depth*Physical_Delta_X  #change from pix to unit
    
    #Assign results to object:
    res = AirScanAnalysisRes(name,transducer_name, unit, im_crop, vert_profile, horizon_profile,
                    S_depth, U_cov, U_skew, U_low, reverb_lines)
    
    
    return res


# #%%


# # path to data:
# #path_data = 'C:/Users/sinkinen/Downloads/keskusröntgen_ilmakuvat/GEMS_IMG/2020_OCT/01/0G155558/'
# path_data = 'C:/Users/sinkinen/US_analysis/data/0G155558/'

# files = [f for f in listdir(path_data) if isfile(join(path_data, f))]

# list_res =  []
# count = 0
# for f in files:
#       data = pydicom.dcmread(path_data+f)
#      # plt.imshow(data.pixel_array, cmap = plt.cm.gray)
#      # plt.title(f+' '+str(count))
#      # plt.show()
#      # input("Press Enter to continue...")
#       count+=1

#       #Test data:
#       #f_t = files[1] #konveksi
#       #f_t = files[7] #tasainen
#       #data = pydicom.dcmread(path_data+f_t)
    
#       # --- Metadata ---  
#       TransducerType = data.TransducerType
#       Physical_Delta_X  = data.SequenceOfUltrasoundRegions[0]['0x0018602c'].value
#       Physical_Delta_Y  = data.SequenceOfUltrasoundRegions[0]['0x0018602e'].value
#       unit = data.SequenceOfUltrasoundRegions[0]['0x00186024'].value
#       name = data[0x00100010].value
#       transducer_name = data[0x00186031].value
     
#       if unit == 3:
#           unit ='cm'
#       else: 
#           unit= 'no meters'
         
#       #Obtain air scan image:        
#       im = data.pixel_array
#       im = rgb2gray(im)   
     
#       if TransducerType == 'CURVED LINEAR': #convex
#           im_t =  transform_convex_image2linear(im)  #transforms to linear
#           im_crop = crop_US_im(im_t, crop2half=False)
#           reverb_lines = 5
         
#       else:
#           im_crop = crop_US_im(im, crop2half=True)
#           reverb_lines = 4
        
#       # --- Analysis ---
#       vert_profile, horizon_profile, S_depth, U_cov, U_skew, U_low = US_air_image_analysis(im_crop, reverb_lines )
     
#       S_depth = S_depth*Physical_Delta_X  #
     
#       #Assign results to object:
#       res = AirScanAnalysisRes(name,transducer_name, unit, im_crop, vert_profile, horizon_profile,
#                       S_depth, U_cov, U_skew, U_low, reverb_lines)
     
#       list_res.append(res)

# #%%



