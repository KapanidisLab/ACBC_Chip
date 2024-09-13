from glob2 import glob
import tifffile
import os
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure
from imgaug import augmenters as iaa
import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing import image

def normalize99(X):
    """normalize image so 0.0 is 0.01st percentile and 1.0 is 99.99th percentile"""

    if np.max(X) > 0:
        X = X.copy()
        v_min, v_max = np.percentile(X[X != 0], (0.1, 99.9))
        X = exposure.rescale_intensity(X, in_range=(v_min, v_max))

    return X

def rescale01(x):
    """normalize image from 0 to 1"""

    if np.max(x) > 0:
        x = (x - np.min(x)) / (np.max(x) - np.min(x))

    return x

def resize_image(image_size, h, w, cell_image_crop, colicoords = False, resize=False):
    
    cell_image_crop = np.moveaxis(cell_image_crop, 0, -1)

    if h < image_size[0] and w < image_size[1]:
        
        seq = iaa.CenterPadToFixedSize(height=image_size[0], width=image_size[1])
 
    else:
        
        if resize == True:
        
            if h > w:
                seq = iaa.Sequential([iaa.Resize({"height": image_size[0], "width": "keep-aspect-ratio"}),
                                      iaa.CenterPadToFixedSize(height=image_size[0],width=image_size[1])])
            else:
                seq = iaa.Sequential([iaa.Resize({"height": "keep-aspect-ratio", "width": image_size[1]}),
                                      iaa.CenterPadToFixedSize(height=image_size[0],width=image_size[1])])
                
        else:
            seq = iaa.Sequential([iaa.CenterPadToFixedSize(height=image_size[0],width=image_size[1]),
                                  iaa.CenterCropToFixedSize(height=image_size[0],width=image_size[1])])

    seq_det = seq.to_deterministic()
    cell_image_crop = seq_det.augment_images([cell_image_crop])[0]
        
        
    cell_image_crop = np.moveaxis(cell_image_crop, -1, 0)
    
    if colicoords:
        if h > w:
            cell_image_crop = np.rot90(cell_image_crop,axes=(1,2))


    return cell_image_crop


def get_images(image_size = (64,64)):
    global image_paths
   
    
    image_list = []
    
    image_size = (64,64)
    
    for image_path in image_paths:
        

        image = tifffile.imread(image_path)
        if image.shape[0] != 3:
            rgb_image = np.zeros([3,image[0].shape[0],image[0].shape[1]])
            
            rgb_image[0] = image[1] # r is now nile red
            rgb_image[1] = image[0] # g is now dapi
            image = rgb_image

        

        #lets_reshuffle
        rgb_image = np.zeros([3,image[0].shape[0],image[0].shape[1]])
        rgb_image[0] = image[1] # r is now dapi
        rgb_image[1] = image[0] # g is nile red
        image = rgb_image

        
        
        
        images = [chan for chan in image]
        
        images.reverse()
        
        for image_index, image in enumerate(images):
            image = normalize99(image)
            image = rescale01(image)
            images[image_index] = image
        
        image_frame = np.zeros_like(images[0])
        images.append(image_frame)
        
        image = np.stack(images)
        

        cell_image_crop = image

        h = image[0].shape[0]
        w = image[0].shape[1]        

        cell_image_crop = resize_image(image_size, h, w, cell_image_crop, resize=True)
        
        
        cell_image_crop = preprocess_image(cell_image_crop)
        
        cell_image_crop = (cell_image_crop*255).astype('uint8')
        #cell_image_crop = np.transpose(cell_image_crop, (1, 2, 0))
        
        image_list.append(cell_image_crop)
        
    return image_list
    
# Function to preprocess the images
def preprocess_image(img):
    # Ensure the image has the shape (H, W, C)
    if img.shape[0] == 3:
        img = np.transpose(img, (1, 2, 0))


    return img


global image_paths
#image_paths = glob(r"E:\dapi classifier paper data\Zagajewski_Data\Zagajewski_Data\Data\MG1655\isolated_cells\sensitive\*.tif")[-100:]

image_paths = glob(r"E:\acbc_revision_experiments\chitosan_cipro\pos*")
#image_paths = glob(r"E:\acbc_revision_experiments\chitosan_untreated\pos*")



image_list = []
phenotype_list = []

image_size = (64,64)

for image_path in image_paths:
    
    (dirname, image_name) = os.path.split(image_path)
    
    image = tifffile.imread(image_path)
    
    phenotype = dirname.split("\\")[-1]
    #phenotype = phenotype.split('_')[1]
    print(phenotype)
    
    if np.min(image) == 0:
        
        mask = np.zeros_like(image[0])
        mask[image[0]==0] = 0
        
        images = [chan for chan in image]
        images.reverse()
        
        for image_index, image in enumerate(images):
            image = normalize99(image)
            image = rescale01(image)
            images[image_index] = image
        
        image_frame = np.zeros_like(images[0])
        images.append(image_frame)
        
        image = np.stack(images)
        
        h, w = image[0].shape[0], image[0].shape[0]
        
        image = resize_image(image_size, h, w, image, resize=True)
        
        
        image = np.transpose(image, (1, 2, 0))
        
        
        image_list.append(image)


        
        







    
# # Step 1: Load the pretrained model
model = tf.keras.models.load_model('MODE - DenseNet121 BS - 16 LR - 0.0005 Holdout test.h5')

target_size = (model.input.shape[1], model.input.shape[2]) 

image_list = get_images(image_size=target_size)   
    

# # Convert list of images to a numpy array
image_list = np.array(image_list)

image_list = np.transpose(image_list,(0,2,3,1))

image_list = image_list[:,:,:,1:]
# # Step 3: Make predictions
predictions = model.predict(image_list)




print(predictions)

# Convert probabilities to labels (0 for resistant class, 1 for sensitive class)
predicted_labels = np.argmax(predictions, axis=1)

# Count the number of each label
num_resistant = np.sum(predicted_labels == 0)
num_sensitive = np.sum(predicted_labels == 1)

print(f"Number of resistant predictions: {num_resistant}")
print(f"Number of sensitive predictions: {num_sensitive}")

print(f"Percentage of sensitive: {num_sensitive/(num_sensitive+num_resistant)}")
    
np.savetxt('predicts.txt',predictions)
    
    
    