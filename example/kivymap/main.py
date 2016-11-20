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
url = "http://build.ees.guru:8888"
api_url = url+"/mines"
markerlist = []
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
                text: "[b]Lille[/b]\\n1 154 861 hab\\n5 759 hab./km2"
                markup: True
                halign: "center"
'''
    
class MapViewApp(App):
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')
    mapview = None
    def build(self):
        gps.configure(on_location=self.on_location,on_status=self.on_status)
        #self.root.add_widget(Builder.load_file('buttons.kv'))
        self.mapview = MapViewer(zoom=15, lat=37.4251096, lon=127.4250295)
        #self.mapview = MapView(zoom=15, lat=50.6494,lon=3.05)
        #gps.start(1000, 0)
        b=MapMark(lat=50.6494,lon=3.057,popup_size= (dp(230), dp(130)),source = "icons/marker2.png")
        #b.add_widget(bubble())
        c=MapMark(lat=50.6294,lon=3.057,popup_size= (dp(230), dp(130)),source = "icons/marker3.png")
        d = Builder.load_string(marker_loader%{"lat":50.6194,"lon":3.057,"source":1})
        self.mapview.add_widget(d)
        self.mapview.add_widget(MapMark(lat=50.6394,lon=3.057,popup_size= (dp(230), dp(130)),source ="icons/marker1.png" ))
        self.mapview.add_widget(b)
        self.mapview.add_widget(c)
        return self.mapview
    
    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])        
        #self.mapview = MapView(zoom=15, lat=kwargs.get('lat'), lon=kwargs.get('lon'))
        self.mapview.center_on(kwargs.get('lat'),kwargs.get('lon'))
        #self.mapview = MapView(zoom=15, lat=37.3251096, lon=127.1250295)

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)
    
    def makemark(self):
        response = requests.post(api_url+"/%(lat)f/%(lon)f/test"%{'lat':self.mapview.lat,'lon':self.mapview.lon},"")        
        status = response.json()['state']
        if status == "FAIL" : 
            return
        response = requests.get(api_url,"")
        for i in response.json():
            global markerlist
            #print "id = %s\tlat,lon = %s,%s\tHP = %s"%(l['idmine'],l['lat'],l['lon'],l['hp'])
            _widget = Builder.load_string(marker_loader%{"lat":i['lat'],"lon":i['lon'],"source":2})
            self.mapview.add_widget(_widget)
            markerlist.append(_widget)
            #self.mapview.add_widget(MapMark(lat=i['lat'],lon=i['lon'] ,   popup_size= (dp(230), dp(130)),source ="icons/marker1.png" ))
        
MapViewApp().run()
