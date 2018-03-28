"""Take a netcdf-4 file (e.g. from OPeNDAP), apply a shift, and output to a GeoTiff.  Currently using the Collection 01
ARD projected coordinate system for the output projection."""

import arcpy
import os
import glob
import argparse

# This is the projected coordinate system used by Collection 01 ARD
# Generated from a reference file with arcpy.Description(<raster>).spatialReference().exporttostring()
wkt = "PROJCS['WGS_1984_Albers',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378140.0,298.257]]," \
      "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['false_easting'," \
      "0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-96.0],PARAMETER['standard_parallel_1'," \
      "29.5],PARAMETER['standard_parallel_2',45.5],PARAMETER['latitude_of_origin',23.0],UNIT['Meter',1.0]];-16901100 " \
      "-6972200 266467840.990852;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision "


def get_files(indir, ext=".nc4"):
    """
    Return a list of files in the specified directory
    :param indir: <str> The full path to the input directory
    :param ext: <str> The file extension, default is .nc4
    :return:
    """
    return glob.glob(indir + os.sep + "*{}".format(ext))


def make_netcdf_raster(in_nc, out_layer, var="band_1", x_dim="easting", y_dim="northing"):
    """
    Execute arcpy MakeNetCDFRasterLayer_md
    :param in_nc: <str> The full path to the input nc file
    :param out_layer: <str> The temporary output raster layer
    :param var: <str> An identifying variable, default is band_1
    :param x_dim: <str> The identifier x-dimension, default is easting
    :param y_dim: <str> The identifier y-dimension, default is northing
    :return:
    """
    arcpy.MakeNetCDFRasterLayer_md(in_netCDF_file=in_nc,
                                   variable=var,
                                   x_dimension=x_dim,
                                   y_dimension=y_dim,
                                   out_raster_layer=out_layer)

    return None


def shift(in_tif, out_tif, x_shift, y_shift):
    """
    Execute arcpy Shift_management
    :param in_tif: <str> The full path to the input tif file
    :param out_tif: <str> The full path to the output tif file
    :param x_shift: <int> The amount to shift x
    :param y_shift: <int> The amount to shift y
    :return:
    """
    arcpy.Shift_management(in_raster=in_tif, out_raster=out_tif, x_value=x_shift, y_value=y_shift)

    return None


def set_prj(in_tif, srs=wkt):
    """
    Get a spatial reference object, read in a projection, apply it to an input tif file
    :param in_tif: <str> The full path to the input tif file
    :param srs: <str> A string containing the projection
    :return:
    """
    sr = arcpy.SpatialReference()

    sr.loadFromString(srs)

    arcpy.DefineProjection_management(in_dataset=in_tif, coor_system=sr)

    return None


def main_work(indir, outdir, x_shift=15, y_shift=-15):
    """
    Get the input files, parse through them and generate outputs
    :param x_shift: <int> Amount to shift x-direction, default is 15
    :param y_shift: <int> Amount to shift y-direction, default is -15
    :param indir: <str> The full path to the input directory
    :param outdir: <str> The full path to the output directory
    :return:
    """

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    nc_files = get_files(indir=indir)

    for nc in nc_files:
        temp_file = outdir + os.sep + os.path.basename(nc).split(".")[0] + "_temp.tif"

        out_file = outdir + os.sep + os.path.basename(nc).split(".")[0] + ".tif"

        print("Working on file %s" % os.path.basename(nc))

        make_netcdf_raster(in_nc=nc, out_layer=temp_file)

        print("Created NetCDF Raster Layer")

        shift(in_tif=temp_file, out_tif=out_file, x_shift=x_shift, y_shift=y_shift)

        print("Performed shift")

        set_prj(in_tif=out_file)

        print("Set Projection\n")

    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("-i", dest="indir", type=str, required=True,
                        help="The full path to the root input directory")

    parser.add_argument("-o", dest="outdir", type=str, required=True,
                        help="The full path to the output directory")

    parser.add_argument("-x", dest="x_shift", type=int, required=False,
                        help="Optional, the amount to shift in x-direction")

    parser.add_argument("-y", dest="y_shift", type=int, required=False,
                        help="Optional, the amount to shift in y-direction")

    args = parser.parse_args()

    main_work(**vars(args))

    return None


if __name__ == "__main__":
    main()
