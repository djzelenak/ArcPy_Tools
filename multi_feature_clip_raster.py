"""
Use a shapefile with multiple features to clip a raster or multiple rasters.  The script will process all rasters in
the specified input directory.

****Requires the ArcGIS python interpreter****

"""
import os
import arcpy
import argparse
import datetime as dt
from arcpy import env


def get_time():
    """
    Return the current time
    :return:
    """
    return dt.datetime.now()


def get_raster(raster_list, y):
    """
    Ensure we pull the appropriate raster for the given year and don't assume a 1:1 relationship
    between items in raster_list and years.
    :param raster_list:
    :param y:
    :return:
    """
    raster = [r for r in raster_list if str(y) in r]

    if len(raster) > 0:

        # Here I'm assuming:
        # 1.  that each file will contain a unique year, and
        # 2.  there is only 1 year in the filename
        return raster[-1]

    else:

        return None


def main_work(indir, outdir, shp, out_prod, field="id", years=None):
    """

    :param indir:
    :param outdir:
    :param shp:
    :param out_prod:
    :param field:
    :param years:
    :return:
    """
    env.workspace = indir

    env.compression = "NONE"

    split_shape = shp

    in_rasters = arcpy.ListRasters()

    split_field = field

    if years is None:

        years = range(1984, 2016)

    cursor = arcpy.SearchCursor(split_shape)

    for row in cursor:

        current_val = row.getValue(split_field)

        subdir = outdir + os.sep + "block_%s" % current_val

        if not os.path.exists(subdir):
            os.makedirs(subdir)

        for year in years:

            in_rast = get_raster(in_rasters, year)

            if in_rast is None:

                print("Could not find matching raster for year %s" % year)

                continue

            result_name = "%s%s%s_block_%s_%s.tif" % (subdir, os.sep, out_prod, current_val, year)

            if os.path.exists(result_name):

                continue

            # Create feature layer of current clipping polygon
            where_clause = "%s = %s" % (split_field, current_val)

            arcpy.MakeFeatureLayer_management(split_shape, 'currentMask', where_clause)

            arcpy.AddMessage("Processing: " + result_name)

            # Save the clipped raster
            arcpy.Clip_management(
                in_rast,
                rectangle="#",
                out_raster=result_name,
                in_template_dataset='currentMask',
                nodata_value="255",
                clipping_geometry="ClippingGeometry",
                maintain_clipping_extent="MAINTAIN_EXTENT"
            )

            if arcpy.Exists('currentMask'):
                arcpy.Delete_management('currentMask')

    return None


def main():
    """

    :return:
    """
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("-i", dest="indir", required=True, type=str,
                        help="The full path to the input directory that will be used as the Workspace Environment.")

    parser.add_argument("-o", dest="outdir", required=True, type=str,
                        help="The full path to the output directory")

    parser.add_argument("-shp", dest="shp", required=True, type=str,
                        help="The full path to the clipping shapefile")

    parser.add_argument("-f", "--field", dest="field", required=True, type=str,
                        help="The name of the attribute field used to identify the splitting features")

    parser.add_argument("-y", "--years", dest="years", required=False, type=str, nargs="*",
                        help="Optionally specify the target years.")

    parser.add_argument("-n", "--name", dest="out_prod", required=True, type=str,
                        help="Specify the name of the product (e.g. Trends, CoverPrim, etc.)")

    args = parser.parse_args()

    main_work(**vars(args))

    return None


if __name__ == "__main__":
    t1 = get_time()

    main()

    t2 = get_time()

    print("Processing Time: %s " % str(t2 - t1))
