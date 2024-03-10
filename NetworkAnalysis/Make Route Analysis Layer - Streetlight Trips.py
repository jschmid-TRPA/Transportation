#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Name: MakeRouteAnalysisLayer_MultiRouteWorkflow.py
# Description: Calculate trips along network using origin/destination points.
# Requirements: Network Analyst Extension

#Import system modules
import arcpy
from arcpy import env
import datetime
import os

try:
    #Check out Network Analyst license if available. Fail if the Network Analyst license is not available.
    if arcpy.CheckExtension("network") == "Available":
        arcpy.CheckOutExtension("network")
    else:
        raise arcpy.ExecuteError("Network Analyst Extension license is not available.")
    
    #Set environment settings
    output_dir = r"//Trpa-fs01/GIS/PROJECTS/Transportation/Active Transportation/Active_Transportation_Pro"
    #The NA layer's data will be saved to the workspace specified here
    env.workspace = os.path.join(output_dir, "Lime_Data.gdb")
    env.overwriteOutput = True

    #Set local variables
    input_network = r"//Trpa-fs01/GIS/GIS_DATA/Transportation/Basemap Features/Roads/Streets Network Dataset/Archives/Streets.gdb"
    input_gdb = r"//Trpa-fs01/GIS/PROJECTS/Transportation/Active Transportation/Active_Transportation_Pro/Lime_Data.gdb"
    network = os.path.join(input_network, "Streets_ND", "Streets_ND")
    origin_points = os.path.join(input_gdb, "Lime_2022_Origins")
    destination_points = os.path.join(input_gdb, "Lime_2022_Destinations")
    layer_name = "Lime_2022_Trips"
    out_routes_featureclass = "Lime_2022_Trips"
    travel_mode = "Driving Time"
    field_name = "TRIP_ID"
    field_type = "TEXT"

    #Set the time of day for the analysis to 8AM on a generic Monday.
    start_time = datetime.datetime(1900, 1, 1, 8, 0, 0)

    #Create a new Route layer.  Optimize on driving time, but compute the
    #distance traveled by accumulating the Meters attribute.
    result_object = arcpy.na.MakeRouteAnalysisLayer(network, layer_name,
                                        travel_mode, time_of_day=start_time,
                                        accumulate_attributes=["Length"])

    #Get the layer object from the result object. The route layer can now be
    #referenced using the layer object.
    layer_object = result_object.getOutput(0)

    #Get the names of all the sublayers within the route layer.
    sublayer_names = arcpy.na.GetNAClassNames(layer_object)
    #Stores the layer names that we will use later
    stops_layer_name = sublayer_names["Stops"]
    routes_layer_name = sublayer_names["Routes"]
    
    #Add a Address field to the Facilities sublayer of the service area layer.
    #This is done before loading the origin and destinations as stops so that 
    #the address values can be transferred from the input features to the 
    #Facilities sublayer. The service area layer created previously is 
    #referred by the layer object.
    arcpy.na.AddFieldToAnalysisLayer(result_object, routes_layer_name, field_name,
                                     field_type)
    
    #Before loading the origin and destination locations as route stops, set
    #up field mapping.  Map the "Trip_ID" field from the input data to
    #the RouteName property in the Stops sublayer, which ensures that each
    #unique Trip_ID will be placed in a separate route.  Matching
    #Trip_IDs ensures origin points and destinations points will end up in the
    #same route.
    field_mappings = arcpy.na.NAClassFieldMappings(layer_object, stops_layer_name)
    field_mappings["RouteName"].mappedFieldName = "TRIP_ID"

    #Add the origin and destination locations as Stops. The same field mapping
    #works for both input feature classes because they both have a field called
    #"Trip_ID"
    arcpy.na.AddLocations(layer_object, stops_layer_name, origin_points,
                        field_mappings, "")
    arcpy.na.AddLocations(layer_object, stops_layer_name, destination_points,
                        field_mappings, "", append="APPEND")

    #Solve the route layer.
    arcpy.na.Solve(layer_object)

    # Get the output Routes sublayer and save it to a feature class
    routes_sublayer = layer_object.listLayers(routes_layer_name)[0]
    arcpy.management.CopyFeatures(routes_sublayer, out_routes_featureclass)

    print("Script completed successfully")

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print("An error occurred on line %i" % tb.tb_lineno)
    print(str(e))
    


# In[ ]:




