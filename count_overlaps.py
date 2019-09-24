"""Calculate the number of shapes that intersect each shape for a multifeature polygon.

1. Creates a new layer from the full shapefile dataset
2. Parses through each row of the layer and creates a new selection for that row
3. Generates a new spatial selection using the intersection with the currently selected row
4. Calculates the number of features selected by the intersection, appends this value to a list
5. Updates the original shapefile with the count for each row

Note: Must run with the arc python 2.7 interpreter (e.g. C:/Python27/ArcGISx6410.5/python.exe)"""


import os
import argparse
import pickle
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

    if not os.path.exists('overlap_counts.pkl'):
        with arcpy.da.SearchCursor(lyr, ['OID@']) as cursor:
            for row in cursor:
                print("getting count for row {} of {}".format(row[0], total))
                arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", "OBJECTID={}".format(row[0]))

                arcpy.SelectLayerByLocation_management(lyr, "INTERSECT", lyr)

                counts.append(int(arcpy.GetCount_management(lyr).getOutput(0)))

                arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

        with open('overlap_counts.pkl', 'wb') as f:
            pickle.dump(counts, f)

    else:
        with open('overlap_counts.pkl', 'rb') as f:
            counts = pickle.load(f)

    with arcpy.da.UpdateCursor(feature, ['count']) as cursor:
        c = 0
        for row in cursor:
            print('updateding row {} of {}'.format(c+1, total))
            row[0] = counts[c]
            cursor.updateRow(row)
            c+=1

    return None


def cli():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--env', dest='env', metavar='PATH',
                        help='Full path to geodatabase')

    parser.add_argument('--feature', dest='feature', metavar='NAME',
                        help='Name of the feature class in the workspace')

    args = parser.parse_args()

    main(**vars(args))

    return None


if __name__ == '__main__':
    cli()