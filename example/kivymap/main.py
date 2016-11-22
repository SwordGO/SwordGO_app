from mapview import MapView
from mapview import MapMarkerPopup
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, \
    AliasProperty, BooleanProperty, StringProperty
from os.path import join, dirname
from kivy.lang import Builder
from kivy.uix.bubble import Bubble
from kivy.clock import Clock, mainthread
from plyer import gps
import requests
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

Label.font_name = "NotoSansCJKkr-Regular.otf"

url = "http://build.ees.guru:8888"
api_url = url+"/mines"
user_url = url+"/user"
inven_url = url+"/inven"
markerlist = []
GL_USER = 1
class MapMark(MapMarkerPopup):
    def remove_open_status(self):
        if self.is_open and self.placeholder.parent:
            self.is_open = not self.is_open
            super(MapMarkerPopup, self).remove_widget(self.placeholder)
    pass

class MapViewer(MapView):
    def on_touch_down(self, touch):
        self.deletemark()
        return super(MapViewer, self).on_touch_down(touch)


    def deletemark(self):
        global markerlist
        for i in markerlist:
            i.remove_open_status()
        
    pass
whereami_loader = '''
MapMarker:
    lat: %(lat)f
    lon: %(lon)f
    source: "icons/mybeacon.png"
'''    
    
marker_loader_ = '''
MapMarkerPopup:
    lat: %(lat)f
    lon: %(lon)f
    source: "icons/marker%(source)d.png"
    popup_size: dp(230), dp(130)

    Bubble:
        BoxLayout:
            orientation: "horizontal"
            padding: "5dp"
            AsyncImage:
                source: "http://upload.wikimedia.org/wikipedia/commons/9/9d/France-Lille-VieilleBourse-FacadeGrandPlace.jpg"
                mipmap: True
            Label:
                text: "[b]Lille[/b]\\n1 154 861 hab\\n5 759 hab./km2"
                markup: True
                halign: "center"
'''
marker_loader = '''
MapMark:
    lat: %(lat)f
    lon: %(lon)f
    source: "icons/marker%(source)d.png"
    popup_size: dp(230), dp(130)

    Bubble:
        BoxLayout:
            orientation: "horizontal"
            padding: "5dp"
            AsyncImage:
                source: "http://upload.wikimedia.org/wikipedia/commons/9/9d/France-Lille-VieilleBourse-FacadeGrandPlace.jpg"
                mipmap: True
            Label:
                text: "[b]%(user_name)s[/b]%(team_name)s"
                markup: True
                halign: "center"
'''

class MapViewBackground(FloatLayout):
    pass
class MapViewApp(App):
    root = None
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')
    error = StringProperty("ERRRRRRRRRRRRRRRRRRRRROOOOOOOOORRRRRR")
    mapview = None
    
    mineral_cobble = NumericProperty()
    mineral_col = NumericProperty()
    mineral_steel = NumericProperty()
    mineral_gold = NumericProperty()
    
    def build(self):
        try:
            self.root = MapViewBackground()
            gps.configure(on_location=self.on_location,on_status=self.on_status)
            self.mapview = self.root.ids.mv
            response = requests.get(api_url,"")        

                
            for i in response.json():
                global markerlist
                #print "id = %s\tlat,lon = %s,%s\tHP = %s"%(l['idmine'],l['lat'],l['lon'],l['hp'])
                user_id = requests.get(user_url+"/%(user)s/test"%i,"")
                user_id = user_id.json()
                #status2 = user_id.json()['state']
                #if status2 == "FAIL" : 
                #    return
                
                
                _widget = Builder.load_string(marker_loader%{"lat":i['lat'],"lon":i['lon'],"source":user_id['team'],"user_name":user_id['name'], "team_name":user_id['team_name']})
                self.mapview.add_widget(_widget)
                markerlist.append(_widget)
            inven_respone = requests.get(inven_url+"/%d/test"%GL_USER,"")
            self.mineral_cobble = inven_respone.json()[0]['cob']
            self.mineral_col = inven_respone.json()[0]['col']
            self.mineral_steel = inven_respone.json()[0]['steel']
            self.mineral_gold = inven_respone.json()[0]['gold']
            self.start(1000,0)
        except Exception as e:        
            self.error = "                             "+str(e)
        return self.root
    
    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    beacon = None
    @mainthread
    def on_location(self, **kwargs):
    
        if self.beacon: self.beacon.detach()
        self.gps_location = '\n'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])        
        #self.mapview = MapView(zoom=15, lat=kwargs.get('lat'), lon=kwargs.get('lon'))
        self.mapview.center_on(kwargs.get('lat'),kwargs.get('lon'))
        self.beacon = Builder.load_string(whereami_loader%{"lat":kwargs.get('lat'),"lon":kwargs.get('lon')})
        self.mapview.add_widget(self.beacon)
        #self.mapview = MapView(zoom=15, lat=37.3251096, lon=127.1250295)
        
    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)
        
    
    def makemark(self):
        try:
            response = requests.post(api_url+"/%(lat)f/%(lon)f/test"%{'lat':self.mapview.lat,'lon':self.mapview.lon},"")        
            status = response.json()['state']
            if status == "FAIL" : 
                return
            response = requests.get(api_url,"")
            
            for i in response.json():
                global markerlist
                #print "id = %s\tlat,lon = %s,%s\tHP = %s"%(l['idmine'],l['lat'],l['lon'],l['hp'])
                user_id = requests.get(user_url+"/%(user)s/test"%i,"")
                user_id = user_id.json()
                #status2 = user_id.json()['state']
                #if status2 == "FAIL" : 
                #    return
                
                
                _widget = Builder.load_string(marker_loader%{"lat":i['lat'],"lon":i['lon'],"source":user_id['team'],"user_name":user_id['name'], "team_name":user_id['team_name']})
                self.mapview.add_widget(_widget)
                markerlist.append(_widget)
                #self.mapview.add_widget(MapMark(lat=i['lat'],lon=i['lon'] ,   popup_size= (dp(230), dp(130)),source ="icons/marker1.png" ))
        except Exception as e:        
            self.error = "                     "+str(e)
            
    def makemark2(self):
        try:
            response = requests.get(api_url+"/%(lat)f/%(lon)f?around=50"%{'lat':self.mapview.lat,'lon':self.mapview.lon},"")
            response = response.json()
            if not response:
                response = requests.post(api_url+"/%(lat)f/%(lon)f/test"%{'lat':self.mapview.lat,'lon':self.mapview.lon},"")        
                status = response.json()['state']
                if status == "FAIL" : 
                    return
                user_id = requests.get(user_url+"/%d/test"%GL_USER,"")
                user_id = user_id.json()
                _widget = Builder.load_string(marker_loader%{"lat":self.mapview.lat,"lon":self.mapview.lon,"source":user_id['team'],"user_name":user_id['name'], "team_name":user_id['team_name']})
                self.mapview.add_widget(_widget)
                markerlist.append(_widget)
            else :
                self.root.popup.open()
        except Exception as e:        
                self.error = "                             "+str(e)
MapViewApp().run()
