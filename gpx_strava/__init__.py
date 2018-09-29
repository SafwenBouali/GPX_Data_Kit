name = "gpx_strava"

import xml.etree.ElementTree as ET
from datetime import datetime,timedelta
import dateutil.parser
import xml.dom.minidom 



class activity:
    """An activity object with all the necessary operations"""
    
    
    def __datetime_converter(timestamp,to_string=True):
        """if the 'to_string' variable is true, it converts a datetime object
        to a string in the ISO 8601 format with a 'T' as a delimiter.
        else, to converts a string coded in ISO 8601 format to a datetime object."""
        if (to_string):
            return timestamp.isoformat('T')
        else:
            return dateutil.parser.parse(timestamp)

        
    def __parse_gpx_string(data_source,from_file=True):

        if(from_file):
            _trk_seg = ET.parse(data_source).getroot()[0][0]
        else:
            _trk_seg = ET.fromstring(data_source).getroot()[0][0]
        trk_pts = []
        first_stamp = ''
        is_first = True
        for trk_pt in _trk_seg:
            temp_pt = activity.__parse_trkpt(trk_pt,is_first)
            if(is_first):
                first_stamp = temp_pt[3]
                temp_pt[3] = 0
                is_first = False
            else:
                temp_pt[3] = (temp_pt[3] - first_stamp).total_seconds()
            trk_pts.append(temp_pt)
        return (first_stamp,trk_pts)


    def __parse_trkpt(trk_pt,is_first):
        _latitude = trk_pt.attrib['lat']
        _longitude = trk_pt.attrib['lon']
        _elevation = trk_pt[0].text
        _timestamp = datetime_converter(trk_pt[1].text,to_string=False)
        return [_latitude,_longitude,_elevation,_timestamp]


    def __encode_gpx_xml(data_source):

        trk_pts = data_source[1]
        first_stamp = data_source[0]
        is_first = True
        gpx = ET.Element('gpx',attrib={'creator':'StravaGPX'})
        trk = ET.SubElement(gpx,'trk')
        trkseg = ET.SubElement(trk,'trkseg')
        for trk_pt in trk_pts:
            trkseg.append(activity.__encode_trkpt(trk_pt,first_stamp))
        return gpx

    
    def __encode_trkpt(trk_pt,first_stamp):

        temp_pt = ET.Element('trkpt',attrib={'lat':trk_pt[0],'lon':trk_pt[1]})
        _ele = ET.SubElement(temp_pt, 'ele')
        _ele.text = trk_pt[2]
        _time = ET.SubElement(temp_pt, 'time')
        _time.text = datetime_converter(first_stamp + timedelta(seconds = trk_pt[3]))
        return temp_pt

    
    def __init__(self,data_source,from_file=True):

        self.first_stamp,self.trk_points = activity.__parse_gpx_string(data_source,from_file=from_file)
        
    def to_xml(self):
    
        return activity.__encode_gpx_xml((self.first_stamp,self.trk_points))
    
    
    def __str__(self):
        
        return ET.tostring(self.to_xml(), 'unicode', method="xml")
    
    def to_file(self,name):
        
        ET.ElementTree(self.to_xml()).write(name + '.gpx')
