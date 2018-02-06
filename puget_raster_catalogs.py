"""
A command line version of the script that is used by ArcTool 'Animation Raster Catalog'

****Requires the ArcGIS python interpreter****
"""

import arcpy
import os
import datetime as dt
import re
import argparse


def get_time():
    """
    Return the current time
    :return:
    """
    return dt.datetime.now()


def main_work(indir, rc_name, gdb_name="Animations.gdb", outdir = None):
    """
    Generate a raster catalog in a file geodatabase from all rasters in the given input directory
    :param indir:
    :param outdir:
    :param gdb_name:
    :param rc_name:
    :return:
    """
    skip_exist = "SKIP_EXISTING"

    skip_first = "NONE"

    year_field = "Year"

    blocks = ["block_%s_" % i for i in range(1, 36)]

    for block in blocks:


        # Set the current workspace
        # formerly arcpy.GetParameterAsText(0)
        current_look = indir + os.sep + block[:-1]
        arcpy.env.workspace = current_look

        # Set the output directory that will contain the geodatabase
        # formerly arcpy.GetParameterAsText(1)
        if outdir is None:

            subdir = indir

        else:

            subdir = outdir + os.sep + block[:-1]

            if not os.path.exists(subdir):

                os.makedirs(subdir)

        # Name of FileGDB
        # formerly arcpy.GetParameterAsText(2)
        if not os.path.splitext(gdb_name)[1] == ".gdb":
        # if not gdb_name[-4:] == ".gdb":
            # Make sure we have the correct file extension for the geodatabase

            gdb_name = gdb_name + ".gdb"

        file_gdb = subdir + os.sep + gdb_name
        print("File GDB name is: %s" % file_gdb)


        # Name of Raster Catalaog
        # formerly arcpy.GetParameterAsText(3)
        print("Raster Catalog name is %s" % rc_name)

        # Get the list of rasters in the working environment
        rasters = arcpy.ListRasters()

        arcpy.AddMessage("Rasters: %s" % rasters)

        for raster in rasters:

            arcpy.BuildPyramids_management(raster, "", skip_first, "", "", "", skip_exist)

            desc = arcpy.Describe(raster)

            sr = desc.spatialReference

        if not arcpy.Exists(file_gdb):
            arcpy.CreateFileGDB_management(subdir, gdb_name)

            arcpy.AddMessage("FileGDB Created")

        # Create file geodatabase managed Raster Catalog
        arcpy.CreateRasterCatalog_management(file_gdb, rc_name, sr, sr, "", "", "", "", "MANAGED", "")

        arcpy.AddMessage("Raster Catalog Created")

        arcpy.WorkspaceToRasterCatalog_management(current_look, file_gdb + os.sep + rc_name, "", "")

        arcpy.AddMessage("Rasters Loaded")

        arcpy.AddField_management(file_gdb + os.sep + rc_name, year_field, "DATE", "", "", "", "", "")

        arcpy.AddMessage("Year Field Added")

        date_field = "Year"

        cur = arcpy.UpdateCursor(file_gdb + os.sep + rc_name, "")

        # Parse through the rows of the raster catalog and populate the "Year" field with the appropriate date
        for row in cur:

            name = row.getValue("Name")

            years = re.findall(r"\d\d\d\d", name)

            if len(years) == 1:

                year = years[0]

            else:

                year = years[1]

            row.setValue(date_field, r"7/1/%s" % year)

            cur.updateRow(row)

    return None

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", dest="indir", type=str, required=True,
                        help="The full path to the root directory containing block subfolders")

    parser.add_argument("-o", dest="outdir", type=str, required=False,
                        help="The full path to the output directory.  The input directory is"
                             "the default location")

    parser.add_argument("-gdb", dest="gdb_name", type=str, required=False, default="Animations.gdb",
                        help="The name of the file geodatabase.  If it does not already"
                             " exist, then a new one will be created")

    parser.add_argument("-rc", dest="rc_name", type=str, required=True,
                        help="The name of the output raster catalog")

    args = parser.parse_args()

    main_work(**vars(args))


if __name__ == "__main__":
    t1 = get_time()

    main()

    t2 = get_time()

    print("Processing Time: %s" % str(t2 - t1))
