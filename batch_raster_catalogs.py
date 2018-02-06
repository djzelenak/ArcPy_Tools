import subprocess, os

if __name__ == "__main__":

    names = ["CoverSec", "ChangeMap", "ChangeMagMap", "LastChange", "SegLength", "QAMap", "CoverConfPrim", "CoverConfSec"]
    acc_names = ["Change", "Cover"]

    interpreter = r"C:\Python27\ArcGIS10.5\python.exe"

    script = r"C:\Users\dzelenak\PycharmProjects\ArcPy_Tools\puget_raster_catalogs.py"

    for n in names:
        subprocess.call([
            interpreter, script,
            "-i", r"D:\LCMAP\PugetSound\regional\aoi_clipped_blocks" + os.sep + n,
            "-o", r"D:\LCMAP\PugetSound\regional\aoi_clipped_blocks\Animations",
            "-rc", n
        ])

    for n in acc_names:
        subprocess.call([
            interpreter, script,
            "-i", r"D:\LCMAP\PugetSound\regional\aoi_clipped_blocks\AccumulatedChange" + os.sep + n,
            "-o", r"D:\LCMAP\PugetSound\regional\aoi_clipped_blocks\Animations",
            "-rc", "Accum%s" % n
        ])
