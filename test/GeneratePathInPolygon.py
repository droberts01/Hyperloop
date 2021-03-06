import time
import math 
import random
import sys

import mpl_toolkits.basemap.pyproj as pyproj

"""
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

from shapely.ops import cascaded_union
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import Point
"""

t0 = time.time()

def round_nums(listOfNums,ndigits):
    outputList = [round(value, ndigits) for value in listOfNums]
    return outputList    
   
def round_points(listOfPoints,ndigits):
    outputList = [round_nums(point,ndigits) for point in listOfPoints]
    return outputList

def get_distance(start, end):
    xDelta = end[0] - start[0]
    yDelta = end[1] - start[1]
    distance = math.sqrt(math.pow(xDelta,2) + math.pow(yDelta,2))
    return distance 

#print(get_distance(0.0,1.0) == 1.0)
    
def get_angle(start, end):
    xDelta = end[0] - start[0]
    yDelta = end[1] - start[1]
    angleFromAxis = math.atan2(yDelta,xDelta)
    return angleFromAxis

def translate_point(start, point):
    translatedPoint = [point[i] - start[i] for i in range(0,len(start)) ] 
    return translatedPoint

def inverseTranslate_point(start, point):
    inverseTranslatedPoint = [point[i] + start[i] for i in range(0,len(start))]
    return inverseTranslatedPoint
    
def rotate_point(angle, point):
    originalX = point[0]
    originalY = point[1]
    rotatedX = originalX * math.cos(angle) + originalY * math.sin(-angle)
    rotatedY = originalX * math.sin(angle) + originalY * math.cos(angle)
    rotatedPoint = [rotatedX, rotatedY]
    return rotatedPoint

def inverseRotate_point(angle, point):
    inverseRotatedPoint = rotate_point(angle,point)
    return inverseRotatedPoint
    
def scale_point(distance, scale, point):
    scaledPt = [(point[0] / distance) * scale, (point[1] / distance) * scale]   
    return scaledPt

def inverseScale_point(distance, scale, point): 
    invScaledPt = [(point[0] * distance) / scale, (point[1] * distance) / scale]
    return invScaledPt

def transform_point(distance, angle, scale, start, point, ndigits):
    tPoint = translate_point(start, point)
    trPoint = rotate_point(-angle, tPoint)
    trsPoint = scale_point(distance, scale, trPoint)
    transformedPoint = round_nums(trsPoint,ndigits)
    return transformedPoint
    
def transform_object(distance, angle, scale, start, anObject, ndigits):
    transObject = [transform_point(distance, angle, scale, start, point, ndigits) for point in anObject]
    return transObject

def inverseTransform_point(distance, angle, scale, start, trspoint, ndigits):
    trpoint = inverseScale_point(distance, scale, trspoint)
    tpoint = inverseRotate_point(angle, trpoint)
    point = inverseTranslate_point(start, tpoint)
    original = round_nums(point,ndigits)
    return original

def inverseTransform_object(distance, angle, scale, start, anObject, ndigits):
    transObject = [inverseTransform_point(distance, angle, scale, start, point, ndigits) for point in anObject]
    return transObject
    
def create_x_lattice(scale, latticeSize, ndigits):
    numPointsInLattice = int(scale / latticeSize)
    rawXLattice = [ latticeSize * i for i in range(1, numPointsInLattice) ]
    xLattice = round_nums(rawXLattice,ndigits)
    return xLattice
    
def list_to_pairs(inList, cycle):
    pairs = [ [inList[i], inList[i+1]] for i in range(0, len(inList) - 1)]
    if cycle:
        pairs.append([inList[-1], inList[0]])
    return pairs

def is_edge_relevant(edge, xValue):
    firstPointXValue = edge[0][0]
    secondPointXValue = edge[1][0]
    rel = (((firstPointXValue <= xValue and xValue <= secondPointXValue ) or
            (secondPointXValue <= xValue and xValue <= firstPointXValue ) and
                                   firstPointXValue != secondPointXValue))   
    return rel

def relevant_edges_for_xvalue(edgeList, xValue):
    relEdges = [edge for edge in edgeList if is_edge_relevant(edge, xValue)]
    return relEdges
    
def edge_to_slopeIntercept(edge):
    slope = ((edge[1][1] - edge[0][1]) / (edge[1][0] - edge[0][0]))
    intercept = edge[1][1] - slope*edge[1][0]
    slopeIntercept = [slope, intercept]
    return slopeIntercept

def get_intersections(relevantEdges, xValue):
    slopeInts = [edge_to_slopeIntercept(edge) for edge in relevantEdges]
    inters = [slopeInt[0] * xValue + slopeInt[1] for slopeInt in slopeInts]
    return inters
    
def get_maxMin(inputList):
    #print(inputList)
    maxMin = [max(inputList), min(inputList)]
    return maxMin

def truncateUp(inFloat):
    if (int(inFloat) == inFloat):
        outInt = inFloat
    else:        
        if (inFloat > 0):
            outInt = int(inFloat) + 1
        else:
            outInt = int(inFloat)
    return outInt

"""
print(truncateUp(1.0) == 1)
print(truncateUp(1) == 1)
print(truncateUp(0.4) == 1)
print(truncateUp(0.5) == 1)
print(truncateUp(0.6) == 1)
print(truncateUp(-0.4) == 0)
print(truncateUp(-0.5) == 0)
print(truncateUp(-0.6) == 0)
print(truncateUp(-1.0) == -1)
print(truncateUp(-1) == -1)
"""

def truncateDown(inFloat):
    if (int(inFloat) == inFloat):
        outInt = inFloat
    else:        
        if (inFloat > 0):
            outInt = int(inFloat)
        else:
            outInt = int(inFloat) - 1
    return outInt

"""
print(truncateDown(1.0) == 1)
print(truncateDown(0.4) == 0)
print(truncateDown(0.5) == 0)
print(truncateDown(0.6) == 0)
print(truncateDown(-0.4) == -1)
print(truncateDown(-0.5) == -1)
print(truncateDown(-0.6) == -1)
print(truncateDown(-1.0) == -1)
"""

def get_sliceCoordinateAbove(inFloat,sliceSpacing,ndigits):
    roughSliceCoordinate = inFloat/sliceSpacing
    sliceCoordinate = round(roughSliceCoordinate,ndigits)
    sliceCoordinateAbove = truncateUp(sliceCoordinate)
    return sliceCoordinateAbove

"""
print(get_sliceCoordinateAbove(0.3,0.2) == 2)
print(get_sliceCoordinateAbove(0.2,0.2) == 1)
print(get_sliceCoordinateAbove(0.1,0.2) == 1)
print(get_sliceCoordinateAbove(-0.3,0.2) == -1)
print(get_sliceCoordinateAbove(-0.2,0.2) == -1)
print(get_sliceCoordinateAbove(-0.1,0.2) == 0)
"""

def get_sliceCoordinateBelow(inFloat,sliceSpacing,ndigits):
    roughSliceCoordinate = inFloat/sliceSpacing
    sliceCoordinate = round(roughSliceCoordinate,ndigits)
    sliceCoordinateBelow = truncateDown(sliceCoordinate)
    return sliceCoordinateBelow

"""
print(get_sliceCoordinateBelow(0.3,0.2) == 1)
print(get_sliceCoordinateBelow(0.2,0.2) == 1)
print(get_sliceCoordinateBelow(0.1,0.2) == 0)
print(get_sliceCoordinateBelow(-0.3,0.2) == -2)
print(get_sliceCoordinateBelow(-0.2,0.2) == -1)
print(get_sliceCoordinateBelow(-0.1,0.2) == -1)
print(get_sliceCoordinateBelow(-0.3,0.1) == -3)
"""

def get_closestSlicePointAbove(inFloat,sliceSpacing,ndigits):
    sliceCoordinateAbove=get_sliceCoordinateAbove(inFloat,sliceSpacing,ndigits)
    roughClosestSlicePointAbove = sliceCoordinateAbove * sliceSpacing
    closestSlicePointAbove = round(roughClosestSlicePointAbove,ndigits)
    return closestSlicePointAbove

"""
print(get_closestSlicePointAbove(0.3,0.2) == 0.4)
print(get_closestSlicePointAbove(0.2,0.2) == 0.2)
print(get_closestSlicePointAbove(0.1,0.2) == 0.2)
print(get_closestSlicePointAbove(-0.3,0.2) == -0.2)
print(get_closestSlicePointAbove(-0.2,0.2) == -0.2)
print(get_closestSlicePointAbove(-0.1,0.2) == 0.0)
print(get_closestSlicePointAbove(0.3,0.1) == 0.3)
print(get_closestSlicePointAbove(-0.3,0.1) == -0.3)
"""

def get_closestSlicePointBelow(inFloat,sliceSpacing,ndigits):
    sliceCoordinateBelow=get_sliceCoordinateBelow(inFloat,sliceSpacing,ndigits)
    roughClosestSlicePointBelow = sliceCoordinateBelow * sliceSpacing
    closestSlicePointBelow = round(roughClosestSlicePointBelow,ndigits)
    return closestSlicePointBelow

"""
print(get_closestSlicePointBelow(0.3,0.2) == 0.2)
print(get_closestSlicePointBelow(0.2,0.2) == 0.2)
print(get_closestSlicePointBelow(0.1,0.2) == 0.0)
print(get_closestSlicePointBelow(-0.3,0.2) == -0.4)
print(get_closestSlicePointBelow(-0.2,0.2) == -0.2)
print(get_closestSlicePointBelow(-0.1,0.2) == -0.2)
print(get_closestSlicePointBelow(0.3,0.1) == 0.3)
print(get_closestSlicePointBelow(-0.3,0.1) == -0.3)
"""

def move_maxMin_onto_slice(maxMin,sliceSpacing,ndigits):
    maxVal = maxMin[0]
    minVal = maxMin[1]
    maxOnSliceInPolygon=get_closestSlicePointBelow(maxVal,sliceSpacing,ndigits)
    minOnSliceInPolygon=get_closestSlicePointAbove(minVal,sliceSpacing,ndigits)
    maxMinOnSlice = [maxOnSliceInPolygon,minOnSliceInPolygon]
    return maxMinOnSlice 

"""
print(move_maxMin_onto_slice([0.5,0.1],0.2) == [0.4,0.2])
print(move_maxMin_onto_slice([0.5,0.2],0.2) == [0.4,0.2])
print(move_maxMin_onto_slice([0.4,0.1],0.2) == [0.4,0.2])
print(move_maxMin_onto_slice([0.4,0.2],0.2) == [0.4,0.2])
print(move_maxMin_onto_slice([0.3,0.1],0.1) == [0.3,0.1])
print(move_maxMin_onto_slice([-0.1,-0.3],0.1) == [-0.1,-0.3])
"""

def maxMin_isValid(maxMin):
    maxVal = maxMin[0]
    minVal = maxMin[1]
    gap = (maxVal - minVal)
    isValid = (gap > 0)
    return isValid

"""
print(maxMin_isValid([1.1,1.0]) == True)
print(maxMin_isValid([1.0,1.0]) == False)
print(maxMin_isValid([0.9,1.0]) == False)
"""

def get_sliceBounds(maxMin,initialSliceSpacing,ndigits):
    #print(maxMin)
    currentSliceSpacing = initialSliceSpacing
    maxMinOnSlice = move_maxMin_onto_slice(maxMin,currentSliceSpacing,ndigits)
    isValid = maxMin_isValid(maxMinOnSlice)
    while (not isValid):
        #print(currentSliceSpacing)
        currentSliceSpacing = currentSliceSpacing/2.0
        maxMinOnSlice = move_maxMin_onto_slice(maxMin,currentSliceSpacing,ndigits)
        isValid = maxMin_isValid(maxMinOnSlice)
    sliceBounds = [maxMinOnSlice,currentSliceSpacing]        
    return sliceBounds

"""
print(get_sliceBounds([0.3,0.1],0.2) == [[0.3,0.1],0.1])
print(get_sliceBounds([-0.1,-0.3],0.2) == [[-0.1,-0.3],0.1])
"""

def build_latticeYSlice(sliceBounds,ndigits):
    maxMin = sliceBounds[0]
    maxVal = maxMin[0]
    minVal = maxMin[1]
    sliceSpacing = sliceBounds[1]
    gap = maxVal - minVal
    roughFloatNumPoints = gap/sliceSpacing + 1
    floatNumPoints = round(roughFloatNumPoints,ndigits)
    numPoints = int(floatNumPoints)
    latticeYSlice = [round(minVal + sliceSpacing*index,ndigits) for index in range(0,numPoints)]
    return latticeYSlice

"""
print(build_latticeSlice([[-0.1,-0.3],0.1]) == [-0.3,-0.2,-0.1])
print(build_latticeSlice([[0.3,0.1],0.1]) == [0.1,0.2,0.3])
"""

def add_xValue(latticeYSlice,xValue):
    latticeSlice = [[xValue,yValue] for yValue in latticeYSlice]
    return latticeSlice

"""
print(add_xValue([0.1,0.2,0.3],0.1) == [[0.1,0.1],[0.1,0.2],[0.1,0.3]])
"""

def generate_lattice(polygon,scale,latticeSize,ndigits):
    initialSliceSpacing = latticeSize
    lattice = []
    xLattice = create_x_lattice(scale,latticeSize,ndigits)
    edgeList = list_to_pairs(polygon, False)
    for xValue in xLattice:
        relevantEdges = relevant_edges_for_xvalue(edgeList, xValue)
        roughIntersections = get_intersections(relevantEdges, xValue)
        intersections = round_nums(roughIntersections,ndigits)
        maxMin = get_maxMin(intersections)
        sliceBounds = get_sliceBounds(maxMin,initialSliceSpacing,ndigits)
        latticeYSlice = build_latticeYSlice(sliceBounds,ndigits)
        latticeSlice = add_xValue(latticeYSlice,xValue)
        lattice.append(latticeSlice)
    return lattice

def lattice_to_plotLattice(lattice):
    xValues = []
    yValues = []
    for latticeSlice in lattice:
        for point in latticeSlice:
            xValues.append(point[0])
            yValues.append(point[1])
    return [xValues,yValues]

def lists_to_tuples(lists):
    tuples = [tuple(eachList) for eachList in lists]
    return tuples

def edge_to_vector(edge):
    firstPoint = edge[0]
    secondPoint = edge[1]
    firstX = firstPoint[0]
    secondX = secondPoint[0]
    firstY = firstPoint[1]
    secondY = secondPoint[1]
    vector = [secondX - firstX, secondY - firstY]
    return vector

def create_vectors(edges):
    vectors = [edge_to_vector(edge) for edge in edges]
    return vectors

def create_vector_pairs(vectors):
    vectorPairs = list_to_pairs(vectors, False)
    return vectorPairs

def get_deltaTheta_between_vectorPair(vectorPair):
    firstVector = vectorPair[0]
    secondVector = vectorPair[1]
    theta1 = math.atan2(firstVector[1], firstVector[0])
    theta2 = math.atan2(secondVector[1], secondVector[0])
    deltaTheta = abs(theta2 - theta1)
    return deltaTheta

def vecPair_deltaTheta_valid(vectorPair, allowedDegreeRange):
    deltaTheta = get_deltaTheta_between_vectorPair(vectorPair)
    vectorPairDeltaThetaValid = (deltaTheta <= math.radians(allowedDegreeRange))
    return vectorPairDeltaThetaValid

def is_route_deltaTheta_valid(route, degreeRange):
    routeDeltaThetaValid = True
    edges = list_to_pairs(route,True)
    vectors = create_vectors(edges)
    vectorPairs = create_vector_pairs(vectors)
    for vecPair in vectorPairs:
        vecPairDeltaThetaValid = vecPair_deltaTheta_valid(vecPair, degreeRange)
        routeDeltaThetaValid = (routeDeltaThetaValid and vecPairDeltaThetaValid)
    return routeDeltaThetaValid

def create_codes(route, isPolygon):
    numEdges = len(route) - isPolygon
    codes = [Path.MOVETO]
    for edgeNum in range(1, numEdges):
        codes.append(Path.LINETO)
    return codes

def unzip_polygon(polygon):
    xValues = []
    yValues = []
    for point in polygon:
        xValues.append(point[0])
        yValues.append(point[1])
    return [xValues, yValues]

def get_bounding_box(polygon):
    values = unzip_polygon(polygon) 
    xValues = values[0]
    yValues = values[1]
    xRange = get_maxMin(xValues)
    yRange = get_maxMin(yValues)
    return [xRange, yRange]

def get_latticeHeights(lattice):
    latticeHeights = [len(latticeSlice) for latticeSlice in lattice]
    return latticeHeights

def generate_validRoutes(lattice, degreeRange):
    validRoutes = []
    latticeHeights = get_latticeHeights(lattice)
    currentPath = [0 for latticeSlice in lattice]
    endPath = [latticeHeight - 1 for latticeHeight in latticeHeights]
    while (currentRoute != endRoute):
        if is_route_deltaTheta_valid(currentRoute, degreeRange):
            validRoutes.append(currentRoute)
        currentRoute = incrementPath(currentRoute)
    return validRoutes

def get_last_edge(route): 
    lastEdge = [route[-2], route[-1]]
    return lastEdge

def get_validRange(lastEdge, accAngle, latticeSlice):
    angleInRadians = math.radians(accAngle)
    sliceHeight = len(latticeSlice)
    lastVector = edge_to_vector(lastEdge)
    lastPoint = lastEdge[1]
    lastYVal = lastPoint[1]
    lastDeltaY = lastVector[1]
    lastDeltaX = lastVector[0]
    lastAngle = math.atan2(lastDeltaY, lastDeltaX)
    upAngle = lastAngle + angleInRadians
    downAngle = lastAngle - angleInRadians
    if upAngle >= math.pi/2:
        yMaxPoint = latticeSlice[sliceHeight - 1]
        yMax = yMaxPoint[1]
    else:
        upSlope = math.tan(upAngle)
        stepUp = upSlope * LATTICE_SIZE
        rawYMax = lastYVal + stepUp
        yMax = value_to_lattice(rawYMax, 0)
    if downAngle <= -math.pi/2:
        yMinPoint = latticeSlice[0]
        yMin = yMinPoint[1]
    else:
        downSlope = math.tan(downAngle)
        stepDown = downSlope * LATTICE_SIZE
        rawYMin = lastYVal + stepDown
        yMin = value_to_lattice(rawYMin, 1)
    validRange = [point for point in latticeSlice if (point[1] <= yMax and point[1] >= yMin)]
    return validRange

def get_trialPoint(isStart,maxAttempts,lastEdge,accAngle,currentSlice):
    if isStart:
        trialPoint = random.choice(currentSlice) 
    else:
        attempt = 0
        trialPointRange=get_validRange(lastEdge,accAngle,currentSlice)
        rangeEmpty = (len(trialPointRange) == 0)
        while (rangeEmpty and attempt < maxAttempts):
            trialPointRange=get_validRange(lastEdge,accAngle,currentSlice)
            rangeEmpty = (len(trialPointRange) == 0)        
            attempt += 1
        if rangeEmpty:
            trialPoint = None
        else:            
            trialPoint = random.choice(trialPointRange)
    return trialPoint

def construct_trialRoute(isStart,maxLength,maxAttempts,lastEdge,accAngle,lattice,sliceIndex):
    trialRoute = []
    trialRouteLength = len(trialRoute)        
    attempt = 0
    while (trialRouteLength < maxLength and attempt < maxAttempts):
        if (isStart and trialRouteLength == 0): 
            isStartNow = True
            lastEdgeNow = lastEdge
        else:
            if (trialRouteLength == 0): 
                lastEdgeNow = lastEdge
            if (trialRouteLength == 1):
                if isStartNow:
                    lastPointinRoute = [0,0]
                else:                    
                    lastPointinRoute = lastEdge[1]
                firstPointinTrialRoute = trialRoute[0]
                lastEdgeNow = [lastPointinRoute,firstPointinTrialRoute]
            if (trialRouteLength >= 2):
                lastEdgeNow = get_last_edge(trialRoute)
            isStartNow = False                
        trialRouteLength = len(trialRoute)        
        sliceIndexNow = sliceIndex + trialRouteLength      
        currentSliceNow = lattice[sliceIndexNow]
        trialPoint = get_trialPoint(isStartNow,maxAttempts,lastEdgeNow,accAngle,currentSliceNow)
        if (trialPoint == None and trialRouteLength == 0):
            trialRoute = None
            break
        if (trialPoint == None):
            attempt += 1
            discardedPoint = trialRoute.pop()
            print("removed point")
            trialRouteLength = len(trialRoute)                    
        else:
            trialRoute.append(trialPoint)
            trialRouteLength = len(trialRoute)                    
    if (trialRouteLength == 0):
        trialRoute = None
    return trialRoute

def choose_valid(lookaheadDepth,maxAttempts,isStart,lastEdge,accAngle,lattice,sliceIndex):   
    latticeLen = len(lattice)
    stepsLeft = latticeLen - sliceIndex
    maxLength = min([stepsLeft, lookaheadDepth])
    attempt = 0
    trialRoute = construct_trialRoute(isStart,maxLength,maxAttempts,lastEdge,accAngle,lattice,sliceIndex)
    while (trialRoute == None and attempt < maxAttempts):
        attempt += 1
        trialRoute = construct_trialRoute(isStart,maxLength,maxAttempts,lastEdge,accAngle,lattice,sliceIndex)
        print("constructs a trialRoute")
    if (trialRoute == None):
        print("Failed to find valid Point")
        sys.exit()
    else:
        print("trialRoute")
        print(trialRoute)
        validPoint = trialRoute[0]
    return validPoint

def smart_add(route,lookaheadDepth,maxAttempts,accAngle,lattice,sliceIndex):
    if len(route) == 1:
        lastEdge = []
        isStart = True
    else:        
        lastEdge = get_last_edge(route)
        isStart = False
    validChoice = choose_valid(lookaheadDepth,maxAttempts,isStart,lastEdge,accAngle,lattice,sliceIndex)     
    route.append(validChoice)
    return route

def smartgen_random_route(lookaheadDepth,maxAttempts,accAngle,lattice):
    latticeLen = len(lattice)
    route = []
    start = [0,0]
    end = [SCALE,0]
    route.append(start)
    for sliceIndex in range(0, latticeLen):
        route = smart_add(route,lookaheadDepth,maxAttempts,accAngle, lattice, sliceIndex)
        #print("route")
        #print(route)
    route.append(end)        
    return route

def gen_randomRoute(lattice,scale):
    route = [[0,0]]
    for latticeSlice in lattice:
        route.append(random.choice(latticeSlice))
    route.append([scale,0])
    return route

def load_listOfPoints(fileName):
    pointsFile = open(fileName,'r')
    stringListOfPoints = pointsFile.read()
    listOfPoints = eval(stringListOfPoints)
    return listOfPoints

def road_to_polygonTuples(road,polygonDegree):
    numPolygons = len(road) - polygonDegree + 1
    polygonTuples = [road[i:i+polygonDegree] for i in range(0,numPolygons)]
    return polygonTuples

def tuples_to_shapelyPolygons(tuples):
    polygons = [Polygon(eachTuple) for eachTuple in tuples]
    return polygons

def cleanPolygons(polygons):
    cleanedPolygons = [polygon.buffer(0.0) for polygon in polygons]    
    return cleanedPolygons

def road_to_boundingPolygon(road,polygonDegree):
    polygonTuples = road_to_polygonTuples(road,polygonDegree)
    polygons = tuples_to_shapelyPolygons(polygonTuples)
    cleanedPolygons = cleanPolygons(polygons)
    boundingPolygon = cascaded_union(cleanedPolygons)
    boundingPolygonCoords = list(boundingPolygon.exterior.coords)
    return boundingPolygonCoords

def scaleUp_point(inPoint, scaleFactor):
    outPoint = [value * scaleFactor for value in inPoint]
    return outPoint

def scaleUp_list_of_points(inList,scaleFactor):
    outList = [scaleUp_point(point,scaleFactor) for point in inList]
    return outList

def scaleDown_point(inPoint, scaleFactor):
    outPoint = [value / scaleFactor for value in inPoint]
    return outPoint

def scaleDown_list_of_points(inList,scaleFactor):
    outList = [scaleDown_point(point,scaleFactor) for point in inList]
    return outList    

def omerc_proj(startLonLat, endLonLat):
    startLon, startLat = startLonLat
    startLatStr = str(startLat)
    startLonStr = str(startLon)
    endLon, endLat = endLonLat
    endLatStr = str(endLat)
    endLonStr = str(endLon)
    centerLat = (startLat + endLat)/2.0
    centerLatStr = str(centerLat)
    centerLon = (startLon + endLon)/2.0
    centerLonStr = str(centerLon)
    omerc=pyproj.Proj('+proj=omerc +lon_0=' + centerLonStr + ' +lat_0=' + centerLatStr  + ' +lon_2=' + endLonStr + ' +lat_2= ' + endLatStr + ' +lon_1=' + startLonStr + ' +lat_1=' + startLatStr)
    return omerc

def mrlc_proj():
    mrlc=pyproj.Proj("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs")
    return mrlc

def lonlat_to_xy(lonlat,proj):
    lon, lat = lonlat
    xy = proj(lon, lat)
    return xy

def xy_to_lonlat(xy,proj):
    x, y = xy
    lonlat = proj(x, y, inverse=True)
    return lonlat

def lonlatList_to_xyList(lonlatList,proj):
    xyList = [lonlat_to_xy(lonlat,proj) for lonlat in lonlatList]
    return xyList   

def xyList_to_lonlatList(xyList,proj):
    lonlatList = [xy_to_lonlat(xy) for xy in xyList]
    return lonlatList

def latlon_to_lonLat(latlon):
    lonlat = [latlon[1], latlon[0]]
    return lonlat

def latlonList_to_lonlatList(latlonList):
    lonlatList = [latlon_to_lonLat(latlon) for latlon in latlonList]
    return lonlatList

origin = 'Los_Angeles'
destination = 'San_Francisco'
ndigits = 6
scale = math.pow(10, 4)
latticeSize = 1.0
scaleDown = math.pow(10,6)

boundingPolygonFileName = origin + 'To' + destination + 'BoundingPolygon.txt'
boundingPolygon = load_listOfPoints(boundingPolygonFileName)

EndpointCoordinatesFileName = origin + 'To' + destination + 'scaledEndpointCoordinates.txt'
startEndCoords = load_listOfPoints(EndpointCoordinatesFileName)
start, end = startEndCoords
scaledStartEndCoords = scaleDown_list_of_points(startEndCoords,scaleDown)
scaledStart, scaledEnd = scaledStartEndCoords
startLonLat, endLonLat = latlonList_to_lonlatList(scaledStartEndCoords)

omerc = omerc_proj(startLonLat,endLonLat)
distance = get_distance(start,end)
angle = get_angle(start,end)
transformedPolygon = transform_object(distance, angle, scale, start, boundingPolygon, ndigits)

lattice = generate_lattice(transformedPolygon,scale,latticeSize,ndigits)
randomRoute = gen_randomRoute(lattice,scale)
routeInLatLon = inverseTransform_object(distance, angle, scale, start, randomRoute, ndigits)

scaledRoute = scaleDown_list_of_points(routeInLatLon,scaleDown)
routeInLonLat = latlonList_to_lonlatList(scaledRoute)
routeInXY = lonlatList_to_xyList(routeInLonLat,omerc)
#startInXY = routeInXY[0]

#print(boundingPolygon)
#print(startLonLat)
#print(endLonLat)
#print(transformedPolygon)
#print(routeInLatLon)
#print(scaledRoute)
#print(randomRoute)
#print(lattice)
#print(routeInXY)
print(startInXY)



"""
polygonVerts = lists_to_tuples(transformedPolygon)
plottablePolygon = patches.Polygon(polygonVerts, closed = True, fill = False)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.add_patch(plottablePolygon)
boundingBox = get_bounding_box(transformedPolygon)
xRange = boundingBox[0]
yRange = boundingBox[1]
minVal = min([min(xRange) - 1, min(yRange) - 1])
maxVal = max([max(xRange) + 1, max(yRange) + 1])
ax.set_xlim(minVal, maxVal)
ax.set_ylim(minVal, maxVal)
"""


"""
boundingPolygon = road_to_boundingPolygon(ROAD, 4)
transformedPolygon = transform_polygon(START, END, boundingPolygon )



#For treating Polygon as Path

polygonCodes = create_codes(polygonVerts, 1)
polygonCodes.append(Path.CLOSEPOLY)
#print(polygonVerts)
polygonPath = Path(polygonVerts, polygonCodes)




#print(lattice)
#print(get_num_paths(lattice))
#print(lattice[0])
#print(get_lattice_heights(lattice))

#For displaying Lattice
plotLattice = lattice_to_plotLattice(lattice)
xvals = plotLattice[0]
yvals = plotLattice[1]
plt.plot(xvals, yvals, 'ro')
"""

#For displaying Path
"""
route = smartgen_random_route(10,10,70, lattice)
vertices = lists_to_tuples(route)
codes = create_codes(vertices, 0)
path = Path(vertices, codes)
pathPatch = patches.PathPatch(path, lw=2, fill = False)
ax.add_patch(pathPatch)
"""

t1 = time.time()
totalTime = t1 - t0
print(totalTime)
#plt.show()


"""
#print(len(listOfPoints))
#polygonTuples = road_to_polygonTuples(listOfPoints, 4)
#polygons1 = tuples_to_shapelyPolygons(polygonTuples)
#print(polygons1)
#unionedPolygon1 = cascaded_union(polygons1)
#print(unionedPolygon1)
#polygons2 = [Polygon(eachTuple) for eachTuple in polygonTuples]
#print(polygons2)
#polygonsValid = [polygon.is_valid for polygon in polygons2]
#badTuples =[eachTuple for eachTuple in polygonTuples if not Polygon(eachTuple).is_valid]
#print(badTuples)
#print(multiPolygo)
#print(polygonsValid)
#unionedPolygon2 = cascaded_union(polygons2)
#print(unionedPolygon2)
#print(polygonTuples)
firstTuple = polygonTuples[0]
#print(firstTuple)
firstPolygon = Polygon(firstTuple)
#print(firstPolygon)
secondTuple = polygonTuples[1]
#print(secondTuple)
secondPolygon = Polygon(secondTuple)
#print(secondPolygon)
polygons = [firstPolygon, secondPolygon]
unionedPolygon = cascaded_union(polygons)
print(unionedPolygon)
def value_to_lattice(value, shiftUp, sliceSpacing):
    latticeSteps = value/sliceSpacing
    if (value >= 0):
        truncatedLatticeSteps = int(latticeSteps)
    else:        
        truncatedLatticeSteps = int(latticeSteps) - 1       
    shiftedTruncatedLatticeSteps = truncatedLatticeSteps + shiftUp
    shiftedValue = shiftedTruncatedLatticeSteps * sliceSpacing
    return shiftedValue

def onLattice(value,sliceSpacing):
    isOnLattice = (value_to_lattice(value,0,sliceSpacing) == value)
    return isOnLattice

def maxMin_to_lattice(maxMin,sliceSpacing):
    maxVal = maxMin[0]
    minVal = maxMin[1]
    maxOnLattice = value_to_lattice(maxVal,0,sliceSpacing) #problem is here
    if onLattice(minVal,sliceSpacing):
        minOnLattice = value_to_lattice(minVal,0,sliceSpacing)
    else:
        minOnLattice = value_to_lattice(minVal,1,sliceSpacing)
    maxMinOnLattice = [ maxOnLattice, minOnLattice ]
    return maxMinOnLattice
    
def build_lattice_slice(maxMin, xValue):
    maxVal = maxMin[0]
    minVal = maxMin[1]
    sliceSpacing = LATTICE_SIZE
    maxOnLattice, minOnLattice = maxMin_to_lattice(maxMin,sliceSpacing)
    gap = maxOnLattice - minOnLattice
    while (gap <= 0):
        sliceSpacing = sliceSpacing/2
        maxOnLattice, minOnLattice = maxMin_to_lattice(maxMin,sliceSpacing)
        gap = maxOnLattice - minOnLattice
    #print((maxVal - maxOnLattice)/(sliceSpacing))
    #print(gap/sliceSpacing)
    ySteps = int(gap/sliceSpacing) + 1
    latticeYSlice = [minVal + (sliceSpacing * i) for i in range(0, ySteps)]
    latticeSlice = [[xValue, yValue] for yValue in latticeYSlice]        
    return latticeSlice

def generate_lattice(polygon,ndigits):
    lattice = []
    xLattice = create_x_lattice()
    edgeList = list_to_pairs(polygon, False)
    for xValue in xLattice:
        relevantEdges = relevant_edges_for_xvalue(edgeList, xValue)
        roughIntersections = get_intersections(relevantEdges, xValue)
        intersections = round_nums(roughIntersections,ndigits)
        maxMin = get_maxMin(intersections)
        roughLatticeSlice = build_lattice_slice(maxMin, xValue)
        latticeSlice = round_points(roughLatticeSlice,ndigits)
        lattice.append(latticeSlice)
    return lattice    

def get_num_paths(lattice):
    num_paths = 1
    for latticeSlice in lattice:
        num_paths = num_paths * len(latticeSlice)
    return num_paths

def gen_ran_sat_route(degreeRange, lattice):
    testRoute = generate_random_route(lattice)
    while (not is_route_deltaTheta_valid(testRoute, 60)):
        testRoute = generate_random_route(lattice)
    return testRoute

def is_edge_deltaY_valid(edge, allowedRange):
    vector = edge_to_vector(edge)
    yDifference = abs(vector[1])
    edge_valid = yDifference <= allowedRange
    return edge_valid

def is_route_deltaY_valid(route, allowedDeltaYRange):
    routeDeltaYValid = True
    edges = list_to_pairs(route, True)
    for edge in edges:
        currentEdgeDeltaYValid = is_edge_deltaY_valid(edge, allowedDeltaYRange)
        routeDeltaYValid = (routeDeltaYValid and currentEdgeDeltaYValid)
    return routeDeltaYValid

def generate_random_route(lattice):
    route = [[0,0]]
    for latticeSlice in lattice:
        route.append(random.choice(latticeSlice))
    route.append([SCALE,0])        
    return route

def replace_last_point(route, lastValidRange):
    last_point = route.pop()    
    new_point = random.choice(lastValidRange)
    route.append(new_point)
    return route


def lookahead(lookaheadDepth,isStartLastEdge,lastPoint,accAngle,lattice,sliceIndex):
    latticeLen = len(lattice)
    stepsLeft = latticeLen - sliceIndex
    steps = min([stepsLeft, lookaheadDepth])
    latticeInRange = lattice[sliceIndex:sliceIndex+steps]
    
    return     

def nextRange_empty(lastPoint, trialPoint, accAngle, nextSlice):
    potentialEdge = [lastPoint, trialPoint]
    nextRange = get_validRange(potentialEdge, accAngle, nextSlice)
    nextRange_empty = (len(nextRange) == 0)
    return nextRange_empty

def nextRanges_containEmpty(lookaheadDepth,maxAttempts,lastPoint,trialPoint,accAngle,lattice,sliceIndex):
    potentialEdge = [lastPoint, trialPoint]    
    latticeLen = len(lattice)
    stepsLeft = latticeLen - sliceIndex
    maxLength = min([stepsLeft, lookaheadDepth])
    trialRoute = [trialPoint]
    attempt = 0
    while (len(trialRoute) <= trialRouteMaxLength and attempt < maxAttempts):
        currentIndex = sliceIndex + len(trialRoute)
        currentSlice = lattice[currentIndex]
        currentRange = get_validRange(potentialEdge,accAngle,currentSlice)
        currentRange_empty = (len(currentRange) == 0)
        while (currentRange_empty and attempt < maxAttempts):
            trialPoint = get_trialPoint(isStart,lastEdge,accAngle,nextSlice)
            potentialEdge = [lastPoint,trialPoint]
            attempt += 1
            currentRange = get_validRange(potentialEdge,accAngle,currentSlice)
            currentRange_empty = (len(currentRange) == 0)
        if currentRange_empty:

            
    return nextRanges_containEmpty

def choose_valid(lookaheadDepth,attempts,isStart,lastEdge,accAngle,lattice,sliceIndex):   
    lastPoint = [0,0] if isStart else lastPoint = lastEdge[1]
    nextSlice = lattice[sliceIndex]
    trialPoint = get_trialPoint(isStartLastEdge, accAngle, nextSlice)   
    #while nextRange_empty(lastPoint, trialPoint, accAngle, nextSlice):
    while nextRanges_containEmpty(lookaheadDepth,attempts,lastPoint,trialPoint, accAngle,lattice,sliceIndex):    
        trialPoint = get_trialPoint(isStart,lastEdge,accAngle,nextSlice)    
    point = trialPoint        
    return point

    #lastPoint = [0,0] if isStart else lastPoint = lastEdge[1]
    #potentialEdge = [lastPoint, trialPoint]    

def translate_point2(start, point, sign):
    translatedPoint = [point[i] + sign*start[i] for i in range(0,len(start)) ] 
    return translatedPoint
    
def rotate_point2(angle, point, sign):
    effecAngle = angle * sign
    originalX = point[0]
    originalY = point[1]
    rotatedX=originalX*math.cos(effecAngle) + originalY * math.sin(-effecAngle)
    rotatedY=originalX*math.sin(effecAngle) + originalY * math.cos(effecAngle)
    rotatedPoint = [rotatedX, rotatedY]
    return rotatedPoint
    
def scale_point2(effectiveScale, point):
    scaledPt = [val * effectiveScale for val in point]   
    return scaledPt

def transform_point2(effectiveScale, angle, start, point, ndigits,isInverse):
    if isInverse:
        sign = 1.0
        effectiveScale = 1.0 / effectiveScale
        sPoint = scale_point2(effectiveScale, point)
        rsPoint = rotate_point2(angle, sPoint, - sign)
        trsPoint = translate_point2(start, rsPoint, sign)
    else:
        sign = -1.0
        tPoint = translate_point2(start, point, sign)
        trPoint = rotate_point2(angle, tPoint, -sign)
        trsPoint = scale_point2(effectiveScale, trPoint)
    transformedPoint = round_nums(trsPoint,ndigits)
    return transformedPoint
    
def transform_object2(effectiveScale, angle, start, anObject, ndigits,isInverse):
    transObject = [transform_point2(effectiveScale, angle, start, point, ndigits,isInverse) for point in anObject]
    return transObject

point = [5.0, 5.0]
start = [0.0, 0.0]
trans = transform_point2(5.0*math.sqrt(2.0),math.pi/4,start, point, 6, True)
original = transform_point2(5.0*math.sqrt(2.0),math.pi/4,start, trans, 6, False)
print(trans)
print(original)

#effectiveScale = scale / distance
#transformedPolygon = transform_object2(effectiveScale, angle, start,boundingPolygon,ndigits, isInverse=True)
#print(transformedPolygon)
"""

