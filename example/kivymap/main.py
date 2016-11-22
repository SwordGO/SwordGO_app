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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

Label.font_name = "NotoSansCJKkr-Regular.otf"

url = "http://build.ees.guru:8888"
api_url = url+"/mines"
user_url = url+"/user"
inven_url = url+"/inven"
markerdic = {}
GL_USER = 1
GL_REQUIRE_COBBLE = 3
GL_REQUIRE_COL = 3
GL_REQUIRE_STEEL = 3
GL_REQUIRE_GOLD = 3

GL_MINE_DISTANCE = 10
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
        global markerdic        
        for i in markerdic.values():
            i.remove_open_status()

    pass
whereami_loader = '''
MapMarker:
    lat: %(lat)f
    lon: %(lon)f
    source: "icons/mybeacon.png"
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

class MapViewBackground(BoxLayout):
    pass
class MapViewApp(App):
    root = None
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')
    error = StringProperty("ERRRRRRRRRRRRRRRRRRRRROOOOOOOOORRRRRR")
    mapview = None
    is_first_load = True
    mineral_cobble = NumericProperty()
    mineral_col = NumericProperty()
    mineral_steel = NumericProperty()
    mineral_gold = NumericProperty()
    mining_gauge = NumericProperty()
    is_am_i_in_mine = False
    def build(self):
        try:
            self.root = MapViewBackground(orientation='vertical')
            gps.configure(on_location=self.on_location,on_status=self.on_status)
            self.mapview = self.root.ids.mv     
            self.mapview.center_on(37.3206023,127.1286901)
            inven_respone = requests.get(inven_url+"/%d/test"%GL_USER,"")
            self.mineral_cobble = inven_respone.json()[0]['cob']
            self.mineral_col = inven_respone.json()[0]['col']
            self.mineral_steel = inven_respone.json()[0]['steel']
            self.mineral_gold = inven_respone.json()[0]['gold']
            self.start(1000,0)
            self.mining_gauge = 0
            self.root.popup3.open()
        except Exception as e:        
            self.error = str(e) + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            print str(e)
        return self.root
    
    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    beacon = None
    @mainthread
    def on_location(self, **kwargs):
        try:
            if self.beacon: self.beacon.detach()
            self.gps_location = '\n'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])                
            self.mapview.center_on(kwargs.get('lat'),kwargs.get('lon'))
            self.beacon = Builder.load_string(whereami_loader%{"lat":kwargs.get('lat'),"lon":kwargs.get('lon')})
            self.mapview.add_widget(self.beacon)            
            if self.is_first_load : 
                response = requests.get(api_url+"/%(lat)f/%(lon)f?around=1000"%{"lat":self.mapview.lat,"lon":self.mapview.lon },"")
                self.is_first_load = False
            else : 
                response = requests.get(api_url+"/%(lat)f/%(lon)f?around=100"%{"lat":self.mapview.lat,"lon":self.mapview.lon },"")                      
            for i in response.json():
                
                global markerdic
                if i['idmine'] in markerdic:
                    
                    
                    response_idmine = requests.get(api_url+"/%(idmine)d"%i,"")
                    if int(response_idmine.json()['hp']) is int(0):
                        self.mapview.remove_widget(markerdic[i['idmine']]) 
                        self.error = "yes you did it !"
                    
                    pass
                    
                else:
                    
                    user_id = requests.get(user_url+"/%(user)s/test"%i,"")
                    user_id = user_id.json()
                    _widget = Builder.load_string(marker_loader%{"lat":i['lat'],"lon":i['lon'],"source":user_id['team'],"user_name":user_id['name'], "team_name":user_id['team_name']})
                    self.mapview.add_widget(_widget)
                    
                    markerdic[i['idmine']] = _widget
            response = requests.get(api_url+"/%(lat)f/%(lon)f?around=/%(distance)d"%{'lat':self.mapview.lat,'lon':self.mapview.lon,'distance':GL_MINE_DISTANCE},"")
            response = response.json()
            if response :
                self.is_am_i_in_mine = True
            else:
                self.is_am_i_in_mine = False
            
            if self.mining_gauge >= 3 :
                self.mining_gauge = 0
            else:
                self.mining_gauge -= 3
            self.root.popup3.open()
        except Exception as e:        
            self.error = str(e) + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)        
    def makemark(self):
        try:
            
            if self.is_am_i_in_mine :                
                self.mining_gauge += 4
            else :
                self.mining_gauge += 2
                
            if self.mining_gauge >= 10 :
                self.mineral_cobble += 1
                self.mineral_col += 1
                self.mineral_steel += 1
                self.mineral_gold += 1
                self.mining_gauge = 0   
        except Exception as e:        
                self.error = str(e) + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" 
    def makemark2(self):
        try:
            if (self.mineral_cobble >= GL_REQUIRE_COBBLE) and (self.mineral_col >= GL_REQUIRE_COL) and (self.mineral_steel >= GL_REQUIRE_STEEL) and (self.mineral_gold >= GL_REQUIRE_GOLD) :                        
                response = requests.get(api_url+"/%(lat)f/%(lon)f?around=50"%{'lat':self.mapview.lat,'lon':self.mapview.lon},"")
                response = response.json()
                if not response:
                    response2 = requests.post(api_url+"/%(lat)f/%(lon)f/test"%{'lat':self.mapview.lat,'lon':self.mapview.lon},"")        
                    status = response2.json()['state']
                    if status == "FAIL" : 
                        return
                    user_id = requests.get(user_url+"/%d/test"%GL_USER,"")
                    user_id = user_id.json()
                    _widget = Builder.load_string(marker_loader%{"lat":self.mapview.lat,"lon":self.mapview.lon,"source":user_id['team'],"user_name":user_id['name'], "team_name":user_id['team_name']})
                    self.mapview.add_widget(_widget)
                    
                    
                    markerdic[response2.json()['id']] = _widget
                else :
                    self.root.popup.open()
            else :
                self.root.popup2.open()
        except Exception as e:        
                self.error = str(e) + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
                
MapViewApp().run()
