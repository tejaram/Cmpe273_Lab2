import logging
logging.basicConfig(level=logging.DEBUG)
from spyne import Application, rpc, ServiceBase, \
    Integer, Unicode
from spyne import Iterable
from urllib2 import urlopen
import urllib2,cookielib
import json
from spyne.decorator import srpc
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
from datetime import datetime
from collections import OrderedDict
import urllib
import requests
import re
import datetime
import operator


class DangerousStreets(ServiceBase):
    @rpc(str, str, str, _returns=Iterable(Unicode))
    def checkcrime(ctx, lat, lon, radius):
        url = "https://api.spotcrime.com/crimes.json?lat="+str(lat)+"&lon="+str(lon)+"&radius="+str(radius)+"&key=."
        t = requests.get(url)
        newDictionary=json.loads(t.text)
        count = 0
        no_of_crimes = len(newDictionary["crimes"])
        crime_type = []
        dates_needed= []

        for key in newDictionary["crimes"]:
            dt_str = key["date"]
            dt_obj = datetime.datetime.strptime(dt_str, '%m/%j/%y %I:%M %p').time()
            dates_needed.append(dt_obj)

        count_12to3 = 0
        count_3to6 = 0
        count_6to9 = 0
        count_9to12 = 0
        count_12PMto3PM = 0
        count_3PMto6PM = 0
        count_6PMto9PM = 0
        count_9PMto12 = 0

        date_cmp1 = datetime.datetime.strptime('12:00 AM', '%I:%M %p').time()
        date_cmp2 = datetime.datetime.strptime('3:00 AM', '%I:%M %p').time()
        date_cmp3 = datetime.datetime.strptime('6:00 AM', '%I:%M %p').time()
        date_cmp4 = datetime.datetime.strptime('9:00 AM', '%I:%M %p').time()
        date_cmp5 = datetime.datetime.strptime('12:00 PM', '%I:%M %p').time()
        date_cmp6 = datetime.datetime.strptime('3:00 PM', '%I:%M %p').time()
        date_cmp7 = datetime.datetime.strptime('6:00 PM', '%I:%M %p').time()
        date_cmp8 = datetime.datetime.strptime('9:00 PM', '%I:%M %p').time()

        for var_dates in dates_needed:
            if (var_dates > date_cmp1) & (var_dates <=date_cmp2):
                count_12to3+=1
            elif(var_dates > date_cmp2) & (var_dates <=date_cmp3):
                count_3to6+=1
            elif(var_dates > date_cmp3) & (var_dates <=date_cmp4):
                count_6to9+=1
            elif(var_dates > date_cmp4) & (var_dates <=date_cmp5):
                count_9to12+=1
            elif(var_dates > date_cmp5) & (var_dates <=date_cmp6):
                count_12PMto3PM+=1
            elif(var_dates > date_cmp6) & (var_dates <=date_cmp7):
                count_3PMto6PM+=1
            elif(var_dates > date_cmp7) & (var_dates <=date_cmp8):
                count_6PMto9PM+=1
            else:
                count_9PMto12+=1
        
        time_count = {"12:01am-3am":count_12to3,"3:01am-6am":count_3to6,"6:01am-9am":count_6to9,
            "9:01am-12noon":count_9to12,"12:01pm-3pm":count_12PMto3PM,"3:01pm-6pm":count_3PMto6PM,
            "6:01pm-9pm":count_6PMto9PM,"9:01pm-12midnight":count_9PMto12}
            
        

        for key in newDictionary["crimes"]:
            crime_type.append(key["type"])

        a=list(set(crime_type))

        crime_type_dict={}

        for i in range(len(a)):
            for j in range(len(crime_type)):
                if crime_type[j] == a[i]:
                    count+=1    
            crime_type_dict[a[i]]=count  
            print a[i] + ":" + str(count)
            count=0

        address_list=[]
        New_address_list=[]
        for key in newDictionary["crimes"]:
            add_str = key["address"]
            address_list.append(add_str)

        for x in address_list:
            if "OF" in x:
                a=x.split("OF")
                New_address_list.append((a[1]).lstrip())
            elif "BLOCK BLOCK" in x:
                a=x.split("BLOCK BLOCK")
                New_address_list.append((a[1]).lstrip())
            elif "BLOCK" in x:
                a=x.split("BLOCK")
                New_address_list.append((a[1]).lstrip())
            elif "&" in x:
                a=x.split("&")
                New_address_list.append((a[0]).lstrip())
                New_address_list.append((a[1]).lstrip())
            else:
                New_address_list.append((x).lstrip())


        unique_addressList=list(set(New_address_list))

        address_dict1={}

        for i in range(len(unique_addressList)):
            for j in range(len(New_address_list)):
                if New_address_list[j] == unique_addressList[i]:
                    count+=1       
                    
            address_dict1[unique_addressList[i]]=str(count)
            count=0

        sorted_address_dict = sorted(address_dict1.items(), key=operator.itemgetter(1))
        popular_words = sorted(address_dict1, key = address_dict1.get, reverse = True)
        string_popularWords=[]
        for elem in popular_words:
            string_popularWords.append(str(elem))

        top_3 = string_popularWords[:3]

        res_dict = {'total_crime':no_of_crimes,
                     'the_most_dangerous_streets':top_3,
                     'crime_type_count':crime_type_dict,
                     'event_time_count':time_count
                     }
        yield res_dict

app = Application([DangerousStreets],
    tns='spyne.lab2',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument()
)
if __name__ == '__main__':
   
    from wsgiref.simple_server import make_server
    wsgi_app = WsgiApplication(app)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()