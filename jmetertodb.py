import numpy as np
import pandas as pd
import xml.etree.cElementTree as et
from influxdb import InfluxDBClient
import argparse

'''
This file aim to write jmeter rawdata into influxdb. There are two parameters in this file. The description of the parameters is in the following:
xmlfile: The file that you want to write into influxdb.
database: The database in influxdb where you want to store your data. It usually is Workload_rawdata or APIMonitor_rawdata.
'''

parser = argparse.ArgumentParser()
parser.add_argument('-xmlfile', type = str, nargs = '?', help = 'The file that you want to write into influxdb.', default = "result.xml")
parser.add_argument('-database', type = str, nargs = '?', help = 'The database in influxdb where you want to store your data. Workload_rawdata or APIMonitor_rawdata.', default = "Workload_rawdata")
args = parser.parse_args()


parsedXML = et.parse(args.xmlfile)

def getvalueofnode(node):
    """ return node text or None """
    return node.text if node is not None else None
	
dfcols = ['timestamp', 'threadname', 'responsecode', 'label', 
         'success', 'latency', 'idletime', 'responsedata']
df_xml = pd.DataFrame(columns=dfcols)

for node in parsedXML.getroot():
    timestamp = node.attrib.get('ts')
    threadname = node.attrib.get('tn')
    responsecode = node.attrib.get('rc')
    label = node.attrib.get('lb')
    success = node.attrib.get('s')
    latency = node.attrib.get('lt')
    idletime = node.attrib.get('it')
    responsedata = node.find('responseData')

    df_xml = df_xml.append(
            pd.Series([timestamp, threadname, responsecode, label, success, latency, 
                       idletime, getvalueofnode(responsedata)], index=dfcols),
            ignore_index=True)
			
df_xml.fillna("None", inplace = True)
df_xml['fields'] = 'fields'
df_xml.timestamp = df_xml.timestamp.astype(float)

# convert minisecond to nanosecond
df_xml.timestamp = df_xml.timestamp.apply(lambda x:int(x*1e6))
df_xml.set_index('fields', inplace = True)

xml_dict = df_xml.to_dict(orient = 'record')
select_keys = ('threadname', 'responsecode', 'label', 'success', 'idletime', 'responsedata')
result_insert = []
for i in range(len(xml_dict)):
    result_insert.append({"measurement": "jmeter_response",
                          "fields": dict((key, xml_dict[i][key]) for key in select_keys), 
                          "time": xml_dict[i]['timestamp']})

'''Write data to influxdb.'''						  
client = InfluxDBClient(host = '192.168.36.123', port = 8086)
client.switch_database(args.database)
client.write_points(result_insert, protocol = 'json')