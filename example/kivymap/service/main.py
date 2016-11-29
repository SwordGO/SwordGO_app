import requests
import json
import plyer
from time import sleep
from plyer import gps
from jnius import autoclass
from kivy.clock import Clock, mainthread


url = "http://build.ees.guru:8888"
api_url = url+"/mines"
user_url = url+"/user"
inven_url = url+"/inven"
who_url = url+"/whoami"


InputStreamReader = autoclass('java.io.InputStreamReader')
BufferedReader = autoclass('java.io.BufferedReader')
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
UUID = autoclass('java.util.UUID')

def get_socket_stream(name):
    paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
    socket = None
    for device in paired_devices:
        if device.getName() == name:
            socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
            
            reader = InputStreamReader(socket.getInputStream(),'US-ASCII')
            recv_stream2 = BufferedReader(reader)
            send_stream2 = socket.getOutputStream()
            break
    socket.connect()
    return recv_stream2, send_stream2



recv_stream = None
send_stream = None
stream = ''

#136
last_lat = 0.
last_lon = 0.   

GL_MINE_DISTANCE = 10


def on_location2(**kwargs):
    try:
        global last_lat
        global last_lon
        last_lat = kwargs.get('lat')
        last_lon = kwargs.get('lon')
        
        
    except Exception as e:    
        pass
        

def on_status2(stype, status):
    pass
   
 
if __name__ == '__main__':
    who_respone = requests.get(who_url+"/%s"%plyer.uniqueid.id,"")
    class_user_id = who_respone.json()['iduser']
    intaval = 0
    while True:
        
        try:
            recv_stream,send_stream = get_socket_stream('GRX')
            
            break
        except Exception as e:
            break            
            
    gps.configure(on_location=on_location2,on_status=on_status2)
    gps.start(1000, 0)
    
    while True:
    
        #on blue tooth
        if recv_stream.ready():
            
            stream = recv_stream.readLine()
            if not stream:
                continue
            
            response = requests.put(api_url+"/1/10/%s"%str(type(stream)),"")
            if stream.find('SG') >= 0:
                is_am_i_in_mine = False
                response = requests.get(api_url+"/%(lat)f/%(lon)f?around=%(distance)d"%{'lat':last_lat,'lon':last_lon,'distance':GL_MINE_DISTANCE},"")
                response = response.json()
                if response :
                    is_am_i_in_mine = response[0]['idmine']
                else:
                    is_am_i_in_mine = False
            
            

                if is_am_i_in_mine :                 
                            
                    response = requests.put(api_url+"/%d/10/%s"%(is_am_i_in_mine,plyer.uniqueid.id),"")            
                    
                    adder = 2
                else :
                    adder = 1
                    

                
                response = requests.put("http://build.ees.guru:8888/inven/%d/cob/%s?num=%d"%(class_user_id,plyer.uniqueid.id,adder),"")
                status = response.json()['state']
                if status == "FAIL" : 
                    pass
                response = requests.put("http://build.ees.guru:8888/inven/%d/col/%s?num=%d"%(class_user_id,plyer.uniqueid.id,adder),"")
                status = response.json()['state']
                if status == "FAIL" : 
                    pass
                response = requests.put("http://build.ees.guru:8888/inven/%d/steel/%s?num=%d"%(class_user_id,plyer.uniqueid.id,adder),"")
                status = response.json()['state']
                if status == "FAIL" : 
                    pass
                response = requests.put("http://build.ees.guru:8888/inven/%d/gold/%s?num=%d"%(class_user_id,plyer.uniqueid.id,adder),"")
                status = response.json()['state']
                if status == "FAIL" : 
                    pass
            