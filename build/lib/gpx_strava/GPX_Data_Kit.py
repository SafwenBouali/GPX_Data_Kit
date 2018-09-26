from bs4 import BeautifulSoup
from datetime import datetime
import dateutil.parser

__xml_header = """<?xml version="1.0" encoding="UTF-8"?>"""
__gpx_header = """<gpx creator="StravaGPX Android" version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">"""
__metadata_header = """<metadata><time>%s</time></metadata>"""
__trk_header = """<trk><name>%s</name><type>1</type><trkseg>"""
__gpx_footer = """</trkseg></trk></gpx>"""


def datetime_converter(timestamp,to_string=True):
    """if the 'to_string' variable is true, it converts a datetime object
    to a string in the ISO 8601 format with a 'T' as a delimiter.
    else, to converts a string coded in ISO 8601 format to a datetime object."""
    try:
        if (to_string):
            return timestamp.isoformat('T')
        else:
            return dateutil.parser.parse(timestamp)
    except e:
        print('wrong variable type! ' + e)


def create_trkpt(trkpt):
    """
    """
    #[timestamp,[lat,long,elevation]]
    _long = trkpt[1][0]
    _lat = trkpt[1][1]
    _elev = trkpt[1][2]
    _time = trkpt[0]
    return """<trkpt lat=\"""" + str(_lat) + """\" lon=\"""" + str(_long) + """\"><ele>""" + str(_elev) + """</ele><time>""" + datetime_converter(timestamp) + """</time></trkpt>"""

def create_gpx_string(name,trkpts):

    res = __xml_header + __gpx_header + (__metadata_header % datetime_converter(trkpts[0][0])) + (__trk_header % name)
    for trkpt in trkpts:
        res += create_trkpt(trkpt)
    res += __gpx_footer
    return res


def create_file(name,string_data,path=''):

    f = open(path + name, 'w')
    f.write(string_data)
    f.close()


def parse_gpx_string(data):

    soup = BeautifulSoup(data, 'xml.parser')
    res = []
    for trkpt in soup.find_all('trkpt'):
        _lat = float(trkpt.trkpt['lat'][0])
        _lon = float(trkpt.trkpt['lon'][0])
        _elev = float(trkpt.find('ele').get_text())
        _timestamp = datetime_converter(trkpt.find('time').get_text(), to_string=False)
        res.append([_timestamp,[_lat,_lon,_elev]])
    return res


def gpx_data_to_incremental_stamps(data):

    res = []
    first_stamp = data[0][0]
    for trkpt in data:
        _ts = (trkpt[0] - first_stamp).seconds
        res.append([_ts,trkpt[1]])
    return res


def incremental_stamps_to_csv(incremental_stamps,file_name):

    import pandas as pd
    columns = ['timestamp','lat','long','elev']
    data = []
    for trkpt in incremental_stamps:
        elem = []
        elem.append(trkpt[0])
        elem.append(trkpt[1][0])
        elem.append(trkpt[1][1])
        elem.append(trkpt[1][2])
        data.append(elem)
    df = pd.DataFrame(data,columns=columns)
    df.to_csv(file_name)
    return df


def read_file(name,path=''):

    f = open(path + name)
    res = f.read()
    f.close()
    return res
