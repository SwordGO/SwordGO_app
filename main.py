# Author: B&B
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.vkeyboard import VKeyboard
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.button import Button
#from functools import partial
from kivy.config import Config
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy import require
from jnius import autoclass

import threading

# This example uses features introduced in Kivy 1.8.0, namely being able to load
# custom json files from the app folder
require("1.8.0")
Builder.load_file('FriendsScreen.kv')
Builder.load_file('MainScreen.kv')
Builder.load_file('GameStartScreen.kv')
Builder.load_file('MyinfoScreen.kv')

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
            recv_stream = BufferedReader(reader)
            send_stream = socket.getOutputStream()
            break
    socket.connect()
    return recv_stream, send_stream


		
class FriendsScreen(Screen):
    def back(self):
        self.manager.current = "MainScreen"


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
    def FriendsButton(self):
        self.manager.current = "FriendsScreen"
    def GamestartButton(self):
        self.manager.current = "GameStartScreen"
    def MyinfoButton(self):
        self.manager.current = "MyinfoScreen"

class GameStartScreen(Screen):
    def __init__(self, **kwargs):
        super(GameStartScreen, self).__init__(**kwargs)
    def back(self):
        self.manager.current = "MainScreen"
    
        
            
        
class MyinfoScreen(Screen):
    def __init__(self, **kwargs):
        super(MyinfoScreen, self).__init__(**kwargs)
    def back(self):
        self.manager.current = "MainScreen"
    

class TestDemo(App):
    sm = None  # The root screen manager
    recv_stream = None
    send_stream = None
    labeltext = StringProperty()
    th = None
    stream = ''
    
    def build(self):
        self.sm = ScreenManager()        
        self.sm.add_widget(MainScreen(name="MainScreen"))
        self.sm.add_widget(FriendsScreen(name="FriendsScreen"))
        self.sm.add_widget(GameStartScreen(name="GameStartScreen"))
        self.sm.add_widget(MyinfoScreen(name="MyinfoScreen"))
        self.sm.current = "MainScreen"
        self.labeltext = "receiving"
        self.th = threading.Thread(target=self.rec,args=(self,))
        return self.sm
        
    def fuck(self):
        self.recv_stream,self.send_stream = get_socket_stream('linvor')
        self.th.start()
    def test(self):
        self.send_stream.write('hi.\n')
        self.send_stream.flush()
        self.labeltext = "hihi"
    def test2(self):
        self.send_stream.write('i hack.\n')
        self.send_stream.flush()
        self.labeltext = "receiving"
        
    def rec(self, sf):
        
        while True:            
            if sf.recv_stream.ready():                
                stream = sf.recv_stream.readLine()                
                sf.labeltext = stream
                
            
        
if __name__ == "__main__":
    TestDemo().run()

	

