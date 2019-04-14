name = "gpx_strava"

import xml.etree.ElementTree as ET
from datetime import datetime,timedelta
import dateutil.parser
import xml.dom.minidom
import random
import geopy.distance
from xml.dom import minidom
import copy




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

    def __find_by_tag_name(element,tag_name):
        
        for elmnt in element:
            if (elmnt.tag.endswith(tag_name)):
                return elmnt
        print("no " + tag_name + " node found")
        return
    
    def __compare_speed(pt_1,pt_2,speed):
        """return true if the calculated speed is less than the threshold, false otherwise."""
        
        coords_1 = (float(pt_1.attrib['lat']), float(pt_1.attrib['lon']))
        coords_2 = (float(pt_2.attrib['lat']), float(pt_2.attrib['lon']))

        return (geopy.distance.vincenty(coords_1, coords_2).m<(speed*25.0/90.0))
    
    def __parse_gpx(data_source):
        """given gpx data, a string, it parses the data
        into an array of points"""
        
        _gpx = ET.fromstring(data_source)
        ET.register_namespace('gpxtpx',"http://www.garmin.com/xmlschemas/TrackPointExtension/v1") 
        
        
        _root_node = ET.Element('gpx')
        
        _trk_seg = activity.__find_by_tag_name(activity.__find_by_tag_name(_gpx,'trk'),'trkseg')
        
        trk_pts = []
        
        first_stamp = ''
        
        is_first = True
        
        temp_pt = None
        temp_time = None
        
        for trk_pt in _trk_seg:
            temp_pt = trk_pt
            temp_time = activity.__find_by_tag_name(temp_pt,'time')
            if(is_first):
                first_stamp = activity.__datetime_converter(temp_time.text,False)
                temp_time.text = 0
                is_first = False
            else:
                temp_time.text = (activity.__datetime_converter(temp_time.text,False) - first_stamp).total_seconds()
            trk_pts.append(temp_pt)
        return (first_stamp,trk_pts,_root_node,temp_time.text)
    
    def add_seconds(self,seconds_to_add):
        for point in self.trk_points:
            temp_pt = point
            temp_time = activity.__find_by_tag_name(temp_pt,'time') 
            temp_time.text += seconds_to_add
            
    def to_file(self, name=''):
        self.build_xml()
        if(name is ''):
            name = 'activity '+str(datetime.now()).replace(' ','').replace('-','').replace(':','')
        name += ".gpx"
        tree = ET.ElementTree(self.__root_node)
        tree.write(name,encoding='UTF-8', method="xml")
    
    def build_xml(self):
        trk = ET.SubElement(self.__root_node,'trk')
        trkseg = ET.Element('trkseg')
        for point in self.trk_points:
            temp_time = activity.__find_by_tag_name(point,'time')
            temp_time.text = activity.__datetime_converter(self.first_stamp + timedelta(seconds = temp_time.text))
            trkseg.append(point)
        trk.append(trkseg)
        return self.__root_node
    
    
    def __init__(self,data_source,data_type='file',crop_threshold_speed=-1):
        
        
        data = None
        
        if (data_type is 'ready'):
            data = data_source
        else:
            if (data_type is 'file'):
                data = open(data_source).read()
            else:
                data = data_source
            data = activity.__parse_gpx(data.replace('xmlns="http://www.topografix.com/GPX/1/1"', '', 1))
            
        self.first_stamp,self.trk_points,self.__root_node,self.__duration = data
        if (crop_threshold_speed is not -1):
            if (crop_threshold_speed < 1):
                print("speed has to be more than 1 km/h")
            else:
                self.crop(crop_threshold_speed)
        
    
    def crop(self,speed_threshold):
        while(activity.__compare_speed(self.trk_points[0],self.trk_points[1],speed_threshold)):
            del(self.trk_points[0])
        while(activity.__compare_speed(self.trk_points[-1],self.trk_points[-2],speed_threshold)):
            del(self.trk_points[-1])
    
    
    def stitch(activities):

        first_stamp = activities[0].first_stamp
        root_node = activities[0].__root_node
        trk_points = []
        last_total = 0
        for i in range(len(activities)):
            activities[i].add_seconds(last_total)
            trk_points.extend(activities[i].trk_points)
            last_total += activities[i].__duration
        return activity((first_stamp,trk_points,root_node,last_total),data_type="ready")



    def join(activities):
        
        first_stamp = activities[0].first_stamp
        root_node = activities[0].__root_node
        trk_points = []
        last_total = 0
        for i in range(len(activities)):
            activities[i].add_seconds((activities[i].first_stamp-first_stamp).total_seconds())
            trk_points.extend(activities[i].trk_points)
        #last_total data is wrong
        return activity((first_stamp,trk_points,root_node,last_total),data_type="ready")
    
