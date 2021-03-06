from os import path
import zipfile
from os import listdir
import json
import math


def metres2degrees(xylist):
    """
    Convert EPSG:3857 to EPSG:4326

    input:
    ------
    xylist: list [ x, y ] in metres

    output:
    -------
    [ lat, lon ] list in degrees
    """
    x = xylist[0]
    y = xylist[1]
    lon = float(x) * 180.0 / 20037508.34
    lat = math.atan(math.exp(y * math.pi / 20037508.34)) * 360 / math.pi - 90
    # print(lat, lon)
    return [lon, lat]


def getCleanedFeatures(pathToGeoJson):
    fileObj = open(pathToGeoJson, "r")
    file_contents = fileObj.read()
    jsonObj = json.loads(file_contents)
    allFeatures = []

    for feature in jsonObj['features']:
        if feature['geometry']['type'] == 'Polygon':
            coords = feature['geometry']['coordinates']
            newcoords = []
            for coord in coords:
                newsubcoords = []
                for latlon in coord:
                    # print("************")
                    # print(latlon)
                    newlatlon = metres2degrees(latlon)
                    newsubcoords.append(newlatlon)
                # print(newsubcoords)
                newcoords.append(newsubcoords)
            # print(newcoords)
            feature['geometry']['coordinates'] = newcoords
            allFeatures.append(feature)
            # print(jsonObj)
    return allFeatures


def getCleanedGeoJson(folderPath, geoJsonObj):
    allFiles = listdir(folderPath)
    allFeatures = []
    for filename in allFiles:
        if(filename[-7:]) == 'geojson':
            pathToGeoJsonFile = path.join(folderPath, filename)
            cleanedFeatures = getCleanedFeatures(pathToGeoJsonFile)
            # print(cleanedFeatures)
            allFeatures += cleanedFeatures

    geoJsonObj['features'] = allFeatures
    return json.dumps(geoJsonObj)


def manageGis(allFilePaths, RELATIVE_PATH_TO_GIS, RELATIVE_PATH_TO_TARGET_GIS):
    for filePath in allFilePaths:
        fileName = path.basename(filePath)

        pathToSampleGeoJson = path.abspath(RELATIVE_PATH_TO_TARGET_GIS)
        fileObj = open(pathToSampleGeoJson, 'r')
        geoJsonObj = json.loads(fileObj.read())
        fileObj.close()

        if fileName[0:3] == "GIS":
            print("UNZIP-----------------------")
            unzipPath = path.abspath(
                RELATIVE_PATH_TO_GIS + "/" + fileName[0:-4])
            giszip = zipfile.ZipFile(filePath, "r")
            giszip.extractall(unzipPath)
            cleanedGeoJson = getCleanedGeoJson(unzipPath,
                                               geoJsonObj)
            # print(cleanedGeoJson)
            fileObj = open(pathToSampleGeoJson, "w")
            fileObj.write(cleanedGeoJson)
            fileObj.close()
