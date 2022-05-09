import matplotlib.pyplot as plt
import pydicom
import numpy as np
from skimage.measure import label  
import cv2 as cv
from scipy.signal import argrelextrema
from scipy import ndimage
import cv2
try:
    from utils.LUT_table_codes import extract_parameters, get_name_from_df
except:
    from LUT_table_codes import extract_parameters, get_name_from_df
import pandas as pd
import matplotlib as mpl
mpl.rcParams['figure.dpi']= 72


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
    This function crops the ultrasound image to the image content ie. extracts the outer regions of the US dicom image.

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
       
    #--- Pre-process ---        
    BW = im > 0 #Threshold image to find the largest element.
   
    label_im, nb_labels = ndimage.label(BW) #label components
   
    #Check the upper half of image:
    sizes = ndimage.sum(BW[0:int(BW.shape[0]/2),:], label_im[0:int(BW.shape[0]/2),:], range(nb_labels + 1))
    loc = np.argmax(sizes)
    if (loc==0).all(): #if nothign is foudn from the upper image then assing loc to 1
        loc=1

    BW = label_im == loc
       ## Sometimes the upper border may be the largest element which is uncorrect 
    #--> Check if that was selected and correct:
    vals = np.where(BW==1) #locations for largest elements
    y_vals=vals[0]
    if (y_vals == 10).any(): #Tent pixel is still image header  -->border is the largest component so the next biggest component is the actual image regions
        sizes[loc]=0
        loc = np.argmax(sizes) #Find next largest component
        BW = label_im==loc
       
   
    L = BW.astype(float)  
   
    # Crop in row direction to content:
    vals = np.argwhere(L==1)    
    x = vals[:,0]
   
    x_min = np.min(x)
    x_max = L.shape[0]  #np.max(x)
    im_crop = im[x_min:x_max,:]    
    BW = BW[x_min:x_max,:]    
   
    #Crop in column direction to content:
    BW = BW[0:100,:] #take first 100 rows to avoid the colorbar
    L = BW.astype(float)  
    vals = np.argwhere(L==1)    
    y = vals[:,1]
   
    y_min = np.min(y) #find the locations
    y_max = np.max(y)
   
    im_crop = im[x_min:x_max,y_min:y_max]   #cropped image


    if crop2half==True: #Reverberations are present in the upper half of the ultrasound image  
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
    locs = argrelextrema(detrend, np.less) #find extremas
    locs= locs[0]
    XX = locs[0:reverb_lines] + smooth_factor
   
    return XX

def imopen_take_largest(BW, dilate_f=True,  kernel=np.ones((5,5), np.uint8),  iters = 2):
    '''
    Performs erosion, largest component and dilatation

    Parameters
    ----------
    BW: input binary image
    kernel: kernel for erosion and dilatation
    smooth_factor : number of iterations in image erosion and dilatation
         The default is 2.

    Returns
    -------
    BW_new : processed binary image

    '''
    img_erosion = cv2.erode(BW.astype("float"), kernel, iterations=iters) #erode binary image
   
    label_im, nb_labels = ndimage.label(img_erosion) #take largest component
    sizes = ndimage.sum(img_erosion, label_im, range(nb_labels + 1))
    loc = np.argmax(sizes)
    img_erosion = label_im==loc
    img_erosion = img_erosion.astype("bool")
    if dilate_f:
        img_dilation = cv2.dilate(img_erosion.astype("float"), kernel, iterations=iters) #dilate back binary image
        BW_new  =  img_dilation.astype("bool")
    else:
        BW_new  = img_erosion  
    return BW_new 

def transform_convex_image2linear(im):
    '''
    This function transforms the convex transducer image to linear using
    polar transform.

    Parameters
    ----------
    im : convex image

    Returns
    -------
    polar_image : Polar image

    '''

    loop = True
    c = 0
    while loop: #see if else in loop
        BW = im  > 0.5*np.mean(im) #Threshold image
        kernel = np.ones((5,5), np.uint8)
        iters = 3
        dilate_f = False #no dilatation to find the offset value
        BW_new = imopen_take_largest(BW, dilate_f) #This also removes text attached to the border
        BW = BW_new  
        
        #take largest component
        label_im, nb_labels = ndimage.label(BW)
        sizes = ndimage.sum(BW, label_im, range(nb_labels + 1))
        loc = np.argmax(sizes)
        BW = label_im==loc
    
        vals = np.argwhere(BW==1)
       
        x = vals[:,1]
        y = vals[:,0]
        
        y_border = 5
        
        if  (y==y_border).any(): #Check of upper border of the image is detected
            im = im[np.max(y):,:] #remove border by cropping
            # plt.subplot(2,1,1)
            # plt.imshow(im)
            # plt.subplot(2,1,2)
            # plt.imshow(im2)
            # plt.show()
            loop = True  #run again
            c +=1
        elif c > 2:
            break
        else:
            
            loop = False #continue
        
    
    #Next compute radius for finding offset to polar transform:
    #Find transducer edges:
    vals = np.argwhere(BW==1)
   
    x = vals[:,1]
    y = vals[:,0]
    y_max = np.max(y); x_max = np.max(x)     
    y_min = np.min(y); x_min = np.min(x) 
    
    y_min+=1 #increment by one to ensure that two peaks are detected
    inds = np.argwhere(y == y_min) #find indices of the edge
    y_part = y[inds]
    x_part = x[inds]
    

   # x_start = np.min(x_part)
   # x_end = np.max(x_part)
    
    #Find more exact locations of the peaks:
    p = BW[y_min,:]
    x_vals = np.argwhere(p==1)
    
    th = np.mean(x_vals)
    inds_x = np.argwhere(x_vals > th)
    
    x_end = int(np.mean(x_vals[inds_x][:,0]))

    inds_x = np.argwhere(x_vals < th)
    x_start = int(np.mean(x_vals[inds_x][:,0]))
    
    # plt.plot(BW[y_min,:])
    # plt.plot(BW[y_min-1,:], 'k')
    # plt.plot([x_start,x_end], [1.05, 1.05], 'r-')
    # plt.ylim(0.8, 1.1)
    # #plt.xlim(x_end-10, x_end+10)
    # plt.show()
    
    x_length = (x_end - x_start)/2 #segment length in x-direction
    x_pos = int(x_start + x_length)
    ind_s = np.argwhere(x==x_pos)
  
   #  plt.imshow(BW)
   #  plt.plot([x_start,x_end], [y_min-1, y_min-1], 'r.')
   #  plt.scatter(int(x_pos),int(y[ind_s[0]]))
   # # plt.ylim(200,100)
   #  #plt.xlim(int(x_start)-5,int(x_start)+5)
   #  plt.show()
    
    inds = np.argwhere(x == x_pos)
    y_part = y[inds]
    y_end = np.min(y_part)
    
    h = y_end - y_min #segment height

    # Compute radius:
    r = (x_length**2 + h**2)/(2*h) 
    
    offset = int(r - h) 

    
    #Find mask again with dilatation to preserve image regions
    BW = im  > 0.5*np.mean(im) #Threshold image
    kernel = np.ones((3,3), np.uint8)
    iters = 1
    BW = imopen_take_largest(BW, True, kernel, iters)
             
    vals = np.argwhere(BW==1)
   
    x = vals[:,0]
    y = vals[:,1]        
    
    y_min = np.min(y)
    y_max = np.max(y)
    x_min = np.min(x)
    x_max = np.max(x)
   
    #Crop image to content:
    im_crop = im[x_min:x_max,y_min:y_max]
    BW = BW[x_min:x_max,y_min:y_max]
    
    # plt.subplot(2,1,1)
    # #plt.imshow(im[x_min-10:x_max+10,y_min-10:y_max+10])
    # plt.imshow(im_crop)
    # plt.subplot(2,1,2)
    # plt.imshow(BW)
    # #plt.imshow(BW_1[x_min-10:x_max+10,y_min-10:y_max+10])
    # plt.show()
        
    
    x = np.round(im_crop.shape[0]*1)
    im_crop2 = im_crop[ 0:x.astype(int) , :]*BW
    
    
    temp = np.zeros((im_crop2.shape[0]+offset, im_crop2.shape[1]))    
    temp[offset:,:] = im_crop2

    # enlarge to cover whole area:
    temp_disk = np.zeros((2*temp.shape[0], 2*temp.shape[0]))
   
    offset2 = np.round(temp_disk.shape[0]/2)
    offset2 = offset2.astype(int)
    offset3 = np.round(-temp.shape[1]/2 + temp_disk.shape[1]/2)
    offset3 = offset3.astype(int)
    end_loc3 = offset3+temp.shape[1]
    end_loc3 = end_loc3.astype(int)
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


def transform_convex_image2linear_old(im):
    '''
    This function transforms the convex transducer image to linear using
    polar transform.

    Parameters
    ----------
    im : convex image

    Returns
    -------
    polar_image : Polar image

    '''
    #----Pre-crop ---
    loop = True
    c = 0
    while loop: #see if else in loop
    
        BW = im > 0.5*np.mean(im) #Threshold image
        
        kernel = np.ones((5,5), np.uint8)
        iters = 4
        dilate_f = True#no dilatation to find the offset value
        BW_new = imopen_take_largest(BW, dilate_f) #This also removes text attached to the border
        BW = BW_new  
            
        label_im, nb_labels = ndimage.label(BW)
        sizes = ndimage.sum(BW, label_im, range(nb_labels + 1))
        loc = np.argmax(sizes)
        BW = label_im==loc
    
    
        vals = np.argwhere(BW==1)
           
        x = vals[:,1]
        y = vals[:,0]
        
        y_border = 5
        
        if  (y==y_border).any(): #Check of upper border of the image is detected
            im = im[np.max(y):,:] #remove border by cropping
            # plt.subplot(2,1,1)
            # plt.imshow(im)
            # plt.subplot(2,1,2)
            # plt.imshow(im2)
            # plt.show()
            loop = True  #run again
            c +=1
        elif c > 2:
            break
        else:
            
            loop = False #continue
            


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
     
    BW = im_crop[ 0:x.astype(int) , :]  > 0.5*np.mean(im) #Threshold image
    
    label_im, nb_labels = ndimage.label(BW)
    sizes = ndimage.sum(BW, label_im, range(nb_labels + 1))
    loc = np.argmax(sizes)
    BW = label_im == loc


   
    # Find edge pixels using for loop:
    left_vals = np.zeros((40, 2))
    right_vals = np.zeros((40, 2))    
    count=0
    for  row in range(10, 50, 1): #range(10, 100, 1): #this affects how many  edge points are taken 
        profile = BW[row,:]
        loc_l = np.argmax(profile)
        loc_r = np.argmax(np.flipud(profile))
        loc_r  = BW.shape[1]-loc_r
       
        left_vals[count,:] = [row, loc_l]
        right_vals[count,:] = [row, loc_r]
        count+=1
   
    ##sanity check:
  #  plt.imshow(BW)
  #  plt.plot(left_vals[:,1], left_vals[:, 0])
  #  plt.plot(right_vals[:,1], right_vals[:, 0])
  #  plt.show()
   
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
       
    ##sanity check 2
 #   plt. plot(x_r, y_r, 'ko')
 #   plt. plot(x_r, m_r*x_r + b_r)
    #
 #   plt. plot(x_l, y_l, 'ro')
 #   plt. plot(x_l, m_l*x_l + b_l)
    #
  #  plt. plot(x_int, y_int, 'bo')
  #  plt.show()
   
    #take the ole image:
    x = np.round(im_crop.shape[0]*1)
   
    
    BW = im_crop[ 0:x.astype(int) , :]  > 0.5*np.mean(im) #Threshold image
    
    kernel = np.ones((3,3), np.uint8)
    iters = 3
    BW = imopen_take_largest(BW, True, kernel, iters)
    
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
   
    #--- S_depth ---
    S_depth = np.argmin(np.abs(vert_profile-background_value))
   
    #plt.plot(vert_profile)
    #plt.plot([S_depth], [background_value], 'r.')
    #plt.show()
  
    #--- Horizontal profile ---
    #Calculate the reverb lines positions:
    XX = get_reverb_lines(vert_profile, reverb_lines, smooth_factor = 5)
       
    horizon_profile = np.mean(im_crop[0:XX[-1],:], axis = 0)
   
    u = horizon_profile
   
    X_u = np.linspace(0, 100, len(horizon_profile))
   
    #plt.plot(X_u,horizon_profile)
    #plt.show()
   
    #--- parameters evaluated from the horizontal profile ---
    U_cov = 100*(np.std(u)/np.mean(u))
    m3 = (1/len(u))*np.sum((u-np.mean(u))**3)
    m32 = ((1/len(u))*np.sum((u-np.mean(u))**2))**(3/2)
    U_skew = m3/m32
   
    #--- Segments--
    segment = np.array([10, 20, 40, 20, 10])
    U_low = [] #init list
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



def is_convex(image):
    ''' Determines if image is from a convex transducer  and returns boolean value'''
   # import pdb; pdb.set_trace()
    im = crop_US_im(image)
    BW = im > 0
    BW = BW[0:int(0.2*BW.shape[0]),:] #take only 20% of the image size
    ind = np.where(BW == 1)    
    hist, bin_edges = np.histogram(ind[1], 10, density=True) #analyze historgram of the found indices

    #plt.scatter(np.linspace(0,1,len(hist)),hist), plt.show()
     
    val1 = hist[int(len(hist)/2)]
    val2 = hist[1]
    ratio = val1/val2 # for curved transducer ratio decreases
   
    if ratio > 0.98: #manually chosen threshold if transducer is linear the ratio is flat
        return False
   
    return True
       

def MAIN_US_analysis(path_data, path_LUT_table):
    '''
    Main function to perform air scan analysis on image defined on
    path path_data. 

    The analysis is based on publication:
    van Horssen P, Schilham A, Dickerscheid D, et al. Automated quality control of ultrasound based on in-air reverberation patterns. 
    Ultrasound. 2017;25(4):229-238. doi:10.1177/1742271X17733145


    Parameters
    ----------
    path_data : str, path to data
    path_LUT_table: str, path to Look-up-table for transducer names

    Returns
    -------
    res : A dictionary which contains results:
        S_depth: scalar, unit value depth
        U_cov:   scalar, horizontal profile covariance
        U_low:  list, horizontal profile segment 10%, 20%, 40%, 20%, 10%
            MSE minimum for each segment
        U_skew: scalar, horizontal profile skewness
        horiz_profile:  vector, horizontal profile
        vert_profiles: vector, vertical profile
        im: cropped image
        name: name of the device
        transducer_name:  name of the transducer
        reverb_lines:  number of reverberation lines used in analysis
        unit: unit os S_depth
        date: date when the iamge was taken
       
    '''
    # ----Read in data ----:
    data = pydicom.dcmread(path_data, force=True)

    # --- Extract dicom metadata ---  
    try:
        TransducerType = data.TransducerType
    except:

        if(is_convex(data.pixel_array)): #If tag is missing then analyze image which transducer type (convex or linear transducer is)  
            TransducerType = 'CURVED LINEAR'
        else:
            TransducerType = 'LINEAR'
   
    Physical_Delta_X  = data.SequenceOfUltrasoundRegions[0]['0x0018602c'].value
    Physical_Delta_Y  = data.SequenceOfUltrasoundRegions[0]['0x0018602e'].value
   
    unit = data.SequenceOfUltrasoundRegions[0]['0x00186024'].value
    label = data[0x00081010].value
   
    try:
        transducer_name = data[0x00186031].value #read in transducer name
    except:
        # ----- if the name cannot be found --> then search from the look up table (LUT)  for corresponding transducer. 
        df = pd.read_excel(path_LUT_table)
        try:
            df.drop(['Unnamed: 0'], axis = 1, inplace=True)
        except:
            None
        dct_params = extract_parameters(data)
        df1 = pd.DataFrame(data = dct_params)
        transducer_name = get_name_from_df(df, df1) #if the transducer name is not listed 'no name' is annotated

        # ---------------------------------------------------------------------------------------------------------------
    
    try:        
        Transducer_Frequency = data.SequenceOfUltrasoundRegions[0]['0x00186030'].value
    except:
        Transducer_Frequency = '' #if the frequency information missing insert empty string
           

    try:
        department = data[0x00081040].value
    except:
        department ='Institutional_department_unknown'
    try:    
        model = data[0x00081090].value
    except:
        model ='Model_unknown'
        
    name = department + '_' + model+ '_' + label
   
    transducer_name = transducer_name + '_' +str(Transducer_Frequency) #the transcuder name should have name and frequency known!
    
    try:
        date = data[0x00080020].value
    except:
        date = '00000000'

    if unit == 3:
        unit ='cm'
    else:
        unit = 'not in meters'
    # --- End  Extract metadata ---     

    #--- Perform analysis ---
    
    #Get air scan image:        
    im = data.pixel_array
   
    if im.ndim == 3: #if image is not grayscale  transform to grayscale
        im = rgb2gray(im)   


    if TransducerType == 'CURVED LINEAR': #convex
        try:
            im_t =  transform_convex_image2linear(im)  #transforms convex transducer to linear
        except:
            print('Old code used')
            im_t =  transform_convex_image2linear_old(im)
            
        im_crop = crop_US_im(im_t, crop2half = False)
        im_crop = im_crop[:, 3:] #remove manually few pixels from the edge
        reverb_lines = 5 #number of reverberation lines to be detected is set to 5 for all curved linear transducers
       
    else: #linear
        im_crop = crop_US_im(im, crop2half=True)
        reverb_lines = 4 #number of reverberation lines to be detected is set to 4 for all  linear transducers
       
    # --- Analysis ---
    vert_profile, horizon_profile, S_depth, U_cov, U_skew, U_low = US_air_image_analysis(im_crop, reverb_lines )
   
    S_depth = S_depth*Physical_Delta_X  #change from pix to unit
   
    #Return results as dictionary:
    return {'S_depth': S_depth,
           'U_cov': U_cov,
           'U_low': U_low,
           'U_skew': U_skew,
           'horiz_profile': horizon_profile.tolist(),
           'vert_profiles': vert_profile.tolist(),
           'im': im_crop.tolist(),
           'name': name,
           'transducer_name': transducer_name,
           'reverb_lines': reverb_lines,
           'unit': unit,
           'date': date}

if __name__ == "__main__":

    # path_data='.. '
    # path_LUT_table = '.../QA_analysis/LUT.xls'
    # MAIN_US_analysis(path_data, path_LUT_table)
     print('Analysis done!')


