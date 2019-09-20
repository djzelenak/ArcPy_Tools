
import os
import argparse
import arcpy


def make_layer(in_feature, out_lyr, **args):
    arcpy.MakeFeatureLayer_management(in_feature, out_lyr, **args)

    return None


def main(env, feature):
    arcpy.env.workspace = env

    lyr = '{}_lyr'.format(feature)

    make_layer(feature, lyr)

    total = arcpy.GetCount_management(lyr)

    counts = list()

    with arcpy.da.SearchCursor(lyr, ['OID@']) as cursor:
        for row in cursor:
            print("getting count for row {} of {}".format(row[0], total))
            arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", "OBJECTID={}".format(row[0]))

            arcpy.SelectLayerByLocation_management(lyr, "INTERSECT", lyr)

            counts.append(int(arcpy.GetCount_management(lyr).getOutput(0)))

            arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

    with arcpy.da.UpdateCursor(feature, ['count']) as cursor:
        c = 0
        for row in cursor:
            print('updateding row {} of {}'.format(c+1, total))
            row[0] = counts[c]
            cursor.updateRow(row)
            c+=1

    return None


def cli():
    parser = argparse.ArgumentParser()

    parser.add_argument('--env', dest='env', metavar='PATH',
                        help='Full path to geodatabase')

    parser.add_argument('--feature', dest='feature', metavar='NAME',
                        help='Name of the feature class in the workspace')

    args = parser.parse_args()

    main(**vars(args))

    return None


if __name__ == '__main__':
    cli()