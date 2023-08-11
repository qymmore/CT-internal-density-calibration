##
# Import the required modules
import argparse
import ogo_helper as ogo
import os
import sys

from Ogo.ogo.calib.internal_calibration import InternalCalibration

##
# Start Script
ogo.message("Start of Script...")

##
# Set up the argument parser for the Script
parser = argparse.ArgumentParser(description="""This script performs internal density calibration for an input image 
using an input mask of the internal tissues. INPUT: Image (as Dicom or NIFTI), Tissue Mask (as Dicom or NIFTI) OUTPUT: 
Text file of Calibration Parameters and associated information""")

parser.add_argument("image_input",
                    help="DICOM directory or *.nii image file")
parser.add_argument("tissue_mask_input",
                    help="DICOM directory or *.nii mask image of internal tissue mask")

##
# Collect the input arguments
args = parser.parse_args()
image = args.image_input
mask = args.tissue_mask_input

##
# Determine image locations and names of files
image_pathname = os.path.dirname(os.path.abspath(image))
image_basename = os.path.basename(image)
mask_pathname = os.path.dirname(mask)
mask_basename = os.path.basename(mask)

##
# Read input image with correct reader
ogo.message("Reading input image...")
if (os.path.isdir(image)):
    ogo.message("Input image is DICOM")
    imageData = ogo.readDCM(image)
    imageType = 1
else:
    ext = os.path.splitext(image)[1]
    if ext == ".nii" or ext == ".nifti":
        ogo.message("Input image is NIFTI")
        imageData = ogo.readNii(image)
        imageType = 2
    else:
        print(("ERROR: image format not recognized for " + image))
        sys.exit()

##
# Read mask image with correct reader
ogo.message("Reading input mask image...")
if os.path.isdir(mask):
    ogo.message("Input mask is DICOM")
    maskData = ogo.readDCM(mask)

else:
    ext = os.path.splitext(mask)[1]
    if ext == ".nii" or ext == ".nifti":
        ogo.message("Input mask is NIFTI")
        maskData = ogo.readNii(mask)
    else:
        print(("ERROR: image format not recognized for " + mask))
        sys.exit()

##
# Extract internal tissue densities from tissue mask image
ogo.message("Extracting adipose ROI...")
adipose = ogo.maskThreshold(maskData, 1)
adipose_mask = ogo.applyMask(imageData, adipose)
adipose_mean = ogo.imageHistogramMean(adipose_mask)

ogo.message("Extracting air ROI...")
air = ogo.maskThreshold(maskData, 2)
air_mask = ogo.applyMask(imageData, air)
air_mean = ogo.imageHistogramMean(air_mask)

ogo.message("Extracting bone ROI...")
bone = ogo.maskThreshold(maskData, 4)
bone_mask = ogo.applyMask(imageData, bone)
bone_mean = ogo.imageHistogramMean(bone_mask)

ogo.message("Extracting muscle ROI...")
muscle = ogo.maskThreshold(maskData, 5)
muscle_mask = ogo.applyMask(imageData, muscle)
muscle_mean = ogo.imageHistogramMean(muscle_mask)

tissue_HU = [adipose_mean[0], air_mean[0], bone_mean[0], muscle_mean[0]]

##
# Determine the internal tissue calibration parameters
ogo.message("Determining the internal tissue calibration parameters...")
internal_calib = InternalCalibration(adipose_mean[0], air_mean[0], bone_mean[0], muscle_mean[0])
internal_calib.fit()
parameters_dict = internal_calib.get_dict()

##
# Write parameters to output text file
org_fileName = image_basename
if imageType == 2:
    org_fileName = image_basename.replace(".nii", "")

txt_fileName = org_fileName + "_InternalCalib.txt"
ogo.message("Writing parameters to output text file: %s" % txt_fileName)
ogo.writeTXTfile(parameters_dict, txt_fileName, image_pathname)

##
# End of script
ogo.message("End of Script.")
sys.exit()
