"""
Populate an attribute field of a shapefile with the path and filenames of PNGs

****Requires the ArcGIS python interpreter****

"""

import os
import arcpy
import glob
import argparse
import datetime

# A list of blocks following the file naming pattern
BLOCKS = ["block_{}".format(j) for j in range(1, 36)]

# A separate list because Chris's png's spell "block" different >:o
# I know this is an easy fix....
BLCKS = ["blk{}_".format(i) for i in range(1, 36)]


def get_time():
    """
    Return the current time
    :return:
    """
    return datetime.datetime.now()


def get_files(indir, ext='.png', option=''):
    """
    Return a list of the files in the specified directory
    :param ext:
    :param indir:
    :return:
    """
    return glob.glob(indir + os.sep + "*_{}{}".format(option, ext))


def check_field(feature, field, length=100):
    """
    Check if the field exists; if it does not then add it to the feature class
    :param feature:
    :param field:
    :param length:
    :return:
    """
    field_list = arcpy.ListFields(feature)

    exists = False

    for f in field_list:
        if f.name == field:
            exists = True

            print("{} field already exists".format(field))

            break

    if not exists:
        arcpy.AddField_management(feature, field, "TEXT", field_length=(length + 10))

        print("{} field was added".format(field))

    return None


def make_layer(indir, feature):
    """
    Create a layer from the raw shapefile so that it's features can be selected outside of ArcMap
    :param indir:
    :param feature:
    :return:
    """
    feature_layer = "{}{}temp_feature".format(indir, os.sep)

    arcpy.MakeFeatureLayer_management(feature, feature_layer)

    print("Feature layer was created")

    return feature_layer


def get_block(block, file_list):
    """
    Return the appropriate file based on the current block
    :param block:
    :param file_list:
    :return:
    """
    # block = block + "_2000_count"

    for f in file_list:

        if block in os.path.basename(f):

            return f


def main_work(img_dir, feature="trends_used_blocks", field="cnfmat", option=""):
    """

    :param img_dir:
    :param feature:
    :param field:
    :return:
    """
    # Get a list of the PNG files from the img_dir
    image_list = get_files(indir=img_dir, option=option)

    # Check if the field exists in the attribute table, if not then add it as a text field with appropriate length
    check_field(feature, field, len(image_list[0]))

    # Create a layer, necessary for selecting individual features outside of ArcMap
    layer = make_layer(img_dir, feature)

    # Parse through the blocks
    # TODO Write function to find specific block number, and block naming pattern
    for block, blck in zip(BLOCKS, BLCKS):

        # Select the current feature based on the current block
        arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION",
                                                "BlockID = 'trends_{}'".format(block))

        # Get the image associated with the current block
        item = get_block(blck, image_list)

        # Access the attribute table field, the row is the selected feature from 'layer'
        with arcpy.da.UpdateCursor(layer, field) as cursor:

            for row in cursor:
                # Add 'item', in this case a string containing the path and filename of a PNG, to the specified field
                # for the selected row of the attribute table
                row[0] = item

                cursor.updateRow(row)

    return None


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-img", dest="img_dir", type=str, required=True,
                        help="The full path to the folder containing the .PNG files")

    parser.add_argument("-shp", dest="feature", type=str, required=False,
                        help="The full path and filename of the shapefile that will store the .PNG file paths")

    parser.add_argument("-f", dest="field", type=str, required=False,
                        help="The name of the attribute table field to populate")

    parser.add_argument("-opt", dest="option", type=str, required=False,
                        help="Not Required: A distinguishing string to help find the correct PNGs")

    args = parser.parse_args()

    main_work(**vars(args))

    return None


if __name__ == "__main__":
    t1 = get_time()

    main()

    t2 = get_time()

    print("Processing time: {}".format(t2 - t1))
