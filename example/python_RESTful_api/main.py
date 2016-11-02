import requests
url = "http://build.ees.guru:8888"
api_url = url+"/mines"

def print_mines(list):
    for l in list:
        print "id = %s\tlat,lon = %s,%s\tHP = %s"%(l['idmine'],l['lat'],l['lon'],l['hp'])
    print "=================================\n"

print "get"
response = requests.get(api_url,"")
#print response.json()
print_mines(response.json())
lat = response.json()[0]['lat']
lon = response.json()[0]['lon']
lat = float(lat)+0.03
lon = float(lon)+0.03
idmine = response.json()[0]['idmine']

print "post"
response = requests.post(api_url+"/%(lat)f/%(lon)f/test"%locals(),"")
print response.json()
id = response.json()['id']
response = requests.get(api_url,"")
print_mines(response.json())

print "put"
response = requests.put(api_url+"/%(id)s/50/test"%locals(),"")
print response.json()
response = requests.get(api_url,"")
print_mines(response.json())

print "delete"
response = requests.delete(api_url+"/%(id)s/test"%locals())
print response.json()
response = requests.get(api_url,"")
print_mines(response.json())

