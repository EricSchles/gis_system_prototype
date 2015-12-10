#This file will have a set of classes used throughout the program

#Imports for ParsePhoneNumber
import json
import pickle
import requests
import simplejson

#Imports for ParseAddress
import usaddress
from streetaddress import StreetAddressFormatter
from nltk.tag.stanford import StanfordNERTagger as Tagger
from geopy.geocoders import GoogleV3,Nominatim
import nltk
import geopy
import lxml.html

tagger = Tagger('/opt/stanford-ner-2014-08-27/classifiers/english.all.3class.distsim.crf.ser.gz','/opt/stanford-ner-2014-08-27/stanford-ner-3.4.1.jar')

addr_formatter = StreetAddressFormatter()

 
def usaddress_to_dict(text):
    addr = usaddress.parse(text)
    addr = [elem for elem in addr if elem[1] != 'Recipient']
    addr_dict = {}
    for value,key in addr:
        if key in addr_dict.keys():
            addr_dict[key] += " "+value
        else:
            addr_dict[key] = value
    return addr_dict

class Distance:
    def __init__(self,start_addr,destination_addr,start_place=None,destination_place=None):
        self.addr_parser = ParseAddress()
        if start_place:
            self.start_addr = start_addr
            self.start_place = start_place
        else:
            start_addr_dict = usaddress_to_dict(start_addr)
            self.start_place = start_addr_dict["PlaceName"] + " " + start_addr_dict["StateName"] 
            
        if destination_place:
            self.destination_addr = destination_addr
            self.destination_place = destination_place
        else:
            destination_addr_dict = usaddress_to_dict(destination_addr)
            self.destination_place = destination_addr_dict["PlaceName"] + " " + destination_addr_dict["StateName"]
        
        self.start_lat_long = self.addr_parser.parse(start_addr,start_place)
        self.destination_lat_long = self.addr_parser.parse(destination_addr,destination_place)

    def get_driving_directions():
        api_key = pickle.load(open("google_driving.pickle","r"))
        url = "https://maps.googleapis.com/maps/api/directions/json?origin={0}&destination={1}&mode=driving&language=en&key={2}".format(str(self.start_addr),str(self.destination_addr),str(api_key))
        result= simplejson.loads(requests.get(url).text)
        return result

    def get_distance():
        pass


class ParseAddress:
    #If we are pulling this information from an excel document then we'll likely have the address information in an acceptable form
    #Otherwise we'll need to run the text through usaddress or streetaddress
    def __init__(self,from_api=False,from_excel=False):
        self.from_api = from_api
        self.from_excel = from_excel

    def pre_formatter(self,addr,dict_addr):
        if "StreetNamePostType" in dict_addr.keys():
            addr = addr.replace("St","Street")
            addr = addr.replace("St.","Street")
            addr = addr.replace("st","Street")
            addr = addr.replace("st.","street")
        return addr
        
    def place_to_lat_long(self,city,state):
        xml_response = requests.get("http://maps.googleapis.com/maps/api/geocode/xml?address={0}+{1}&sensor=false".format(str(city),str(state))).text
        xml_response = xml_response.split("\n")[1:] #strip header
        xml = lxml.html.fromstring("\n".join(xml_response))
        lat_long = xml.xpath("//geometry/location")[0].text_content().split("\n")
        lat_long = [elem.strip() for elem in lat_long]
        lat_long = [elem for elem in lat_long if elem != '']
        return lat_long

    #The parse will get you a lat/long representation of the address, which exists somewhere in the passed in text.
    #It expects free form text or a complete address
    def parse(self,text,place="NYC"):
        dict_addr,addr_type = self.preprocess(text)
        google_key = pickle.load(open("google_api_key.pickle","r"))
        g_coder = GoogleV3(google_key)
        if addr_type == 'complete':
            combined_addr = []
            keys = ["AddressNumber","StreetName","StreetNamePostType","PlaceName","StateName","ZipCode"]
            for key in keys:
                try:
                    combined_addr += [dict_addr[key]]
                except KeyError:
                    continue
                addr = " ".join(combined_addr) 
            n_coder = Nominatim()
            addr = self.pre_formatter(addr,dict_addr)
            lat_long = n_coder.geocode(addr)
            if lat_long: #means the request succeeded
                return lat_long
            else:
                lat_long = g_coder.geocode(addr)
                return lat_long
            #If None, means no address was recovered.
        if addr_type == 'cross streets':
            #handle case where dict_addr is more than 2 nouns long
	    cross_addr = " and ".join(dict_addr) + place 
            try:
                lat_long = g_coder.geocode(cross_addr)
                return lat_long
            except geopy.geocoders.googlev3.GeocoderQueryError:
                return None
        
    #remove near, split on commas, 
    #tag - div style="padding-left:2em;
    #two possible return "types" - complete a real address or cross streets, which only gives two cross streets and therefore an approximate area
    def preprocess(self,text):
        #this case is included because usaddress doesn't do a great job if there isn't a number at parsing semantic information
        #However if there is a number it tends to be better than streetaddress
        #Therefore usaddress is better at figuring out where the start of an address is, in say a very long body of text with an address in there at some point
        #It isn't that great at approximate locations
        nouns = ['NN','NNP','NNPS','NNS']
        if any([elem.isdigit() for elem in text.split(" ")]):
            addr_dict = usaddress_to_dict(text)
            return addr_dict,"complete"
        else:
            possible_streets = []
            for word,tag in tagger.tag(text.split()):
                if tag == 'LOCATION':
                    possible_streets.append(word)
            parts = nltk.pos_tag(nltk.word_tokenize(text))
            for part in parts:
                if any([part[1]==noun for noun in nouns]):
                    possible_streets.append(part[0])
            return possible_streets,"cross streets"
	 
        #addresses: http://stackoverflow.com/questions/11160192/how-to-parse-freeform-street-postal-address-out-of-text-and-into-components
        #To do: build general list from http://www.nyc.gov/html/dcp/html/bytes/dwnlion.shtml
        #And from https://gis.nyc.gov/gisdata/inventories/details.cfm?DSID=932
        
        #Here I need to add Part of Speech tagging and pull out all the nouns as possible street names.
        #Then I need to come up with a list of street names in NYC and run each noun through the list
        #From there I'll have all the street names
            

    

