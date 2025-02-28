######
#
# run_tf_detector.py
#
# Functions to load a TensorFlow detection model, run inference,
# and render bounding boxes on images.
#
# See the "test driver" cell for example invocation.
#
######

#%% Constants, imports, environment

import urllib.request as urlopen
from io import BytesIO

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import tensorflow as tf
from PIL import Image


#%% Core detection functions

def load_model(checkpoint):
    """
    Load a detection model (i.e., create a graph) from a .pb file
    """

    print('Creating Graph...')
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(checkpoint, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    print('...done')

    return detection_graph



def generate_image_detections(detection_graph, url):
    if isinstance(url, str):
        with detection_graph.as_default():
            with tf.Session(graph=detection_graph) as sess:
                img_file = BytesIO(urlopen.urlopen(url).read())
                image = Image.open(img_file)
                # image = mpimg.imread(url)
                imageNP_expanded = np.expand_dims(image, axis=0)
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                box = detection_graph.get_tensor_by_name('detection_boxes:0')
                score = detection_graph.get_tensor_by_name('detection_scores:0')
                clss = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                
                # Actual detection
                (box, score, clss, num_detections) = sess.run(
                        [box, score, clss, num_detections],
                        feed_dict={image_tensor: imageNP_expanded})

        
                return box[0], score[0], clss[0]
        

def draw_image_detections(boxes, scores, classes, inputFileName, outputFileName, confidenceThreshold=0.9):
    """
    Render bounding boxes on the image files specified in [inputFileNames].  [boxes] and [scores] should be in the format
    returned by generate_detections.
    """
    number_of_det = 0
    bboxes = []


    #Read the image file
    img_file = BytesIO(urlopen.urlopen(inputFileName).read())
    image = Image.open(img_file)

    # image = mpimg.imread(inputFileName)

    iBox = 0; 
    box = boxes[iBox]
    dpi = 100
    s = image.size;         
    imageHeight = s[1]; 
    imageWidth = s[0]
    figsize = imageWidth / float(dpi), imageHeight / float(dpi)

    fig = plt.figure(figsize=figsize)
    ax = plt.axes([0,0,1,1])
    
    # Display the image
    ax.imshow(image)
    ax.set_axis_off()
    for iBox,box in enumerate(boxes):
            score = scores[iBox]
            if score < confidenceThreshold:
                continue

            # top, left, bottom, right 
            #
            # x,y origin is the upper-left
            topRel = box[0]
            leftRel = box[1]
            bottomRel = box[2]
            rightRel = box[3]
            
            x = leftRel * imageWidth
            y = topRel * imageHeight
            w = (rightRel-leftRel) * imageWidth
            h = (bottomRel-topRel) * imageHeight

            bboxes.append({
                'x': x,
                'y': y,
                'w': w,
                'h': h
            })
            
            # Location is the bottom-left of the rect
            #
            # Origin is the upper-left
            iLeft = x
            iBottom = y
            rect = patches.Rectangle((iLeft,iBottom),w,h,linewidth=6,edgecolor='r',facecolor='none')
            
            # Add the patch to the Axes
            ax.add_patch(rect)
            number_of_det += 1

    # This is magic goop that removes whitespace around image plots (sort of)        
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    ax.xaxis.set_major_locator(ticker.NullLocator())
    ax.yaxis.set_major_locator(ticker.NullLocator())
    ax.axis('tight')
    ax.set(xlim=[0,imageWidth],ylim=[imageHeight,0],aspect=1)
    plt.axis('off')                

    # plt.savefig(outputFileName, bbox_inches='tight', pad_inches=0.0, dpi=dpi, transparent=True)
    plt.savefig(outputFileName, dpi=dpi, transparent=True) 
    

    return number_of_det, bboxes

