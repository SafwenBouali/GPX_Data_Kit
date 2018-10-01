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
        else, it converts a string coded in ISO 8601 format to a datetime object."""
        
        if (to_string):
            return timestamp.isoformat('T')
        else:
            return dateutil.parser.parse(timestamp)

        
    def __parse_gpx(data_source,from_file=True):
        """given gpx data, a file or a string, it parses the data
        into an array of points"""
        
        if(from_file):
            _gpx = ET.parse(data_source).getroot()
        else:
            _gpx = ET.fromstring(data_source)
        _trk_seg = _gpx[1][2]
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
        """parses each point into an array, compromised of:
        lat, long, elevation and a timestamp"""
        
        _latitude = trk_pt.attrib['lat']
        _longitude = trk_pt.attrib['lon']
        _elevation = trk_pt[0].text
        _timestamp = activity.__datetime_converter(trk_pt[1].text,to_string=False)
        return [_latitude,_longitude,_elevation,_timestamp]


    def __encode_gpx_xml(data_source):
        """encodes the array of points to an xml ET"""
        
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
        """encodes a point into an XML element"""
        
        temp_pt = ET.Element('trkpt',attrib={'lat':trk_pt[0],'lon':trk_pt[1]})
        _ele = ET.SubElement(temp_pt, 'ele')
        _ele.text = trk_pt[2]
        _time = ET.SubElement(temp_pt, 'time')
        _time.text = activity.__datetime_converter(first_stamp + timedelta(seconds = trk_pt[3]))
        return temp_pt

    
    def __init__(self,data_source,data_type='file'):
        
        if(data_type is 'file'):
            self.first_stamp,self.trk_points = activity.__parse_gpx(data_source)
        elif(data_type is 'str'):
            self.first_stamp,self.trk_points = activity.__parse_gpx(data_source,from_file=False)
        elif(data_type is 'ready'):
            self.first_stamp,self.trk_points = data_source
        
    def to_xml(self):
    
        return activity.__encode_gpx_xml((self.first_stamp,self.trk_points))
    
    
    def __str__(self):
        
        return ET.tostring(self.to_xml(), 'unicode', method="xml")
    
    def to_file(self,name=''):
        
        if(name is ''):
            name = "stitched_activity"
        name += ".gpx"
        ET.ElementTree(self.to_xml()).write(file_or_filename=name)
        
    def add_seconds(self,seconds):
        
        for pt in self.trk_points:
            pt[3] += seconds
        
    def get_last_trk_seconds_count(self):
        
        return self.trk_points[-1][3]
    
    

def stitch_activities(activities):
    """stitches activities into one activity without time lapses in-between.
    assumes that activities has a length of at least 2"""
    
    first_stamp = activities[0].first_stamp
    combined_trk_points = activities[0].trk_points
    for i in range(1,len(activities)):
        activities[i].add_seconds(activities[i-1].get_last_trk_seconds_count())
        combined_trk_points.extend(activities[i].trk_points[1:])
    return activity((first_stamp,combined_trk_points),data_type='ready')
