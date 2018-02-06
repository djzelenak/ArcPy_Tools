import arcpy
import os
import sys

# Get the path to this script's location
relpath = os.path.dirname(sys.argv[0])

# Create final output PDF
pdfPath = relpath + r"\FinalOutput.pdf"

# Overwrite the pre-existing PDF if it exists
if os.path.exists(pdfPath):
    os.remove(pdfPath)

# Create empty PDF document object in memory at the specified path
finalResult = arcpy.mapping.PDFDocumentCreate(relpath + r"\FinalOutput.pdf")

# Reference MXD map document on disk, or use keyword "CURRENT" to use the map document
# currently loaded in ArcMap
mxd = arcpy.mapping.MapDocument("CURRENT")

# Reference the trends used blocks layer
trends_block_layer = arcpy.mapping.ListLayers(mxd, "trends_used_blocks")[0]

# Reference the query layer as the currently viewed trends block
query_layer = arcpy.mapping.ListLayers(mxd, "Current View")[0]

# Reference page layout elements
for elm in arcpy.mapping.ListLayoutElements(mxd):
    if elm.name == "bar1":  bar1 = elm
    if elm.name == "bar2":  bar2 = elm
    if elm.name == "bar1txt":  bar1txt = elm
    if elm.name == "bar2txt":  bar2txt = elm
    if elm.name == "NoGrowth": noGrowth = elm
    if elm.name == "horzLine": horzLine = elm
    if elm.name == "vertLine": vertLine = elm
    if elm.name == "cellTxt":  cellTxt = elm
    if elm.name == "headerTxt": headerTxt = elm

# Reference DDP object
ddp = mxd.dataDrivenPages

# Loop through each DDP page
for pageNum in range(1, mxd.dataDrivenPages.pageCount + 1):
    mxd.dataDrivenPages.currentPageID = pageNum

    # Graphic table variable values
    tableHeight = 3.0
    tableWidth = 2.5
    headerHeight = 0.2
    rowHeight = 0.15
    upperX = 2.8
    upperY = 3.2

    # Build selection set
    stateName = ddp.pageRow.State_Name
    print stateName
    arcpy.SelectLayerByAttribute_management(countyLayer, "NEW_SELECTION",
                                            "\"STATE_NAME\" = '" + stateName + "' AND \"HisPerChange\" > 100")
    numRecords = int(arcpy.GetCount_management(countyLayer).getOutput(0))

    # Sort selection
    arcpy.Sort_management(countyLayer, "in_memory\sort", [["HisPerChange", "ASCENDING"]])

    # Show selected features
    queryLayer.definitionQuery = "\"STATE_NAME\" = '" + stateName + "' AND \"HisPerChange\" > 100"

    # Add note if there are no counties > 100%
    if numRecords == 0:
        noGrowth.elementPositionX = 3
        noGrowth.elementPositionY = 2
    else:
        # if number of rows exceeds page space, resize row height
        if ((tableHeight - headerHeight) / numRecords) < rowHeight:
            headerHeight = headerHeight * ((tableHeight - headerHeight) / numRecords) / rowHeight
            rowHeight = (tableHeight - headerHeight) / numRecords

        # Set and clone vertical line work
        vertLine.elementHeight = headerHeight + (rowHeight * numRecords)
        vertLine.elementPositionX = upperX
        vertLine.elementPositionY = upperY

        temp_vert = vertLine.clone("_clone")
        temp_vert.elementPositionX = upperX + 1.5
        temp_vert = vertLine.clone("_clone")
        temp_vert.elementPositionX = upperX + 2.5

        # Set and clone horizontal line work
        horzLine.elementWidth = tableWidth
        horzLine.elementPositionX = upperX
        horzLine.elementPositionY = upperY

        horzLine.clone("_clone")
        horzLine.elementPositionY = upperY - headerHeight

        y = upperY - headerHeight
        for horz in range(1, numRecords + 1):
            y = y - rowHeight
            temp_horz = horzLine.clone("_clone")
            temp_horz.elementPositionY = y

        # Set header text elements
        headerTxt.fontSize = headerHeight / 0.0155
        headerTxt.text = "County Name"
        headerTxt.elementPositionX = upperX + 0.75
        headerTxt.elementPositionY = upperY - (headerHeight / 2)

        newFieldTxt = headerTxt.clone("_clone")
        newFieldTxt.text = "% Growth"
        newFieldTxt.elementPositionX = upperX + 2

        # Set and clone cell text elements
        cellTxt.fontSize = rowHeight / 0.0155

        y = upperY - headerHeight
        rows = arcpy.SearchCursor("in_memory\sort")
        for row in rows:
            x = upperX + 0.05
            col1CellTxt = cellTxt.clone("_clone")
            col1CellTxt.text = row.getValue("NAME")
            col1CellTxt.elementPositionX = x
            col1CellTxt.elementPositionY = y
            col2CellTxt = cellTxt.clone("_clone")
            col2CellTxt.text = str(round(row.getValue("HisPerChange"), 2))
            col2CellTxt.elementPositionX = x + 1.75
            col2CellTxt.elementPositionY = y
            y = y - rowHeight

    # Modify bar chart
    his2000 = float(mxd.dataDrivenPages.pageRow.HisPer2000)
    bar1.elementHeight = (his2000 / 50) * 2
    bar1txt.text = "(" + str(round(his2000, 2)) + ")"
    bar1txt.elementPositionY = bar1.elementPositionY + bar1.elementHeight + 0.1
    his2010 = float(mxd.dataDrivenPages.pageRow.HisPer2010)
    bar2.elementHeight = (his2010 / 50) * 2
    bar2txt.text = "(" + str(round(his2010, 2)) + ")"
    bar2txt.elementPositionY = bar2.elementPositionY + bar2.elementHeight + 0.1

    # Export to PDF
    ddp.exportToPDF(relpath + r"\temp.pdf", "CURRENT")
    finalResult.appendPages(relpath + r"\temp.pdf")
    os.remove(relpath + r"\temp.pdf")

    # Clean-up before next page
    for elm in arcpy.mapping.ListLayoutElements(mxd, "GRAPHIC_ELEMENT", "*clone*"):
        elm.delete()
    for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*clone*"):
        elm.delete()
    noGrowth.elementPositionX = -3
    cellTxt.elementPositionX = -3
    headerTxt.elementPositionX = -3
    horzLine.elementPositionX = -3
    vertLine.elementPositionX = -3

    arcpy.Delete_management("in_memory\sort")

finalResult.updateDocProperties("Hispanic Growth MapBook", "Esri", "Population", "map sheets, map book", "USE_THUMBS")
finalResult.saveAndClose()
