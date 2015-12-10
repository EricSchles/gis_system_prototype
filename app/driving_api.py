#comes from here: http://stackoverflow.com/questions/17267807/python-google-maps-driving-time
#travel api docs: https://developers.google.com/maps/documentation/directions/intro#traffic-model
#distance api docs: https://developers.google.com/maps/documentation/distance-matrix/intro?hl=en
import simplejson, urllib
import pickle
import requests

#google api
def get_driving_directions(orig_coord,dest_coord):
    api_key = pickle.load(open("google_driving.pickle","r"))
    url = "https://maps.googleapis.com/maps/api/directions/json?origin={0}&destination={1}&mode=driving&language=en&key={2}".format(str(orig_coord),str(dest_coord),str(api_key))
    result= simplejson.load(urllib.urlopen(url))
    return result

def get_driving_dir(orig_coord,dest_coord):
    api_key = pickle.load(open("google_driving.pickle","r"))
    url = "https://maps.googleapis.com/maps/api/directions/json?origin={0}&destination={1}&mode=driving&language=en&key={2}".format(str(orig_coord),str(dest_coord),str(api_key))
    result= simplejson.loads(requests.get(url).text)
    return result
