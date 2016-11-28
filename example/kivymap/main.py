from mapview import MapView
from mapview import MapMarkerPopup
from mapview.geojson import GeoJsonMapLayer
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
import json
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from plyer import accelerometer
import plyer

Label.font_name = "NotoSansCJKkr-Regular.otf"

url = "http://build.ees.guru:8888"
api_url = url+"/mines"
user_url = url+"/user"
inven_url = url+"/inven"
geo_url = url+"/geo"
who_url = url+"/whoami"
markerdic = {}
GL_REQUIRE_COBBLE = 3
GL_REQUIRE_COL = 3
GL_REQUIRE_STEEL = 3
GL_REQUIRE_GOLD = 3
GL_SHAKE_SCALE = 5
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
    
team_color = ['grey','blue','green','hotpink']

geo_header = '{"type": "FeatureCollection","features": ['
geo_body = '''{
      "type": "Feature",
      "properties": {        
        "color": "%s"        
      },
      "geometry": %s
      },'''
geo_footer = ''']
}'''  


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
                text: "[b]%(hp)d [/b]%(team_name)s"
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
    sensorEnabled = False
    last_val = None
    old_layer = None
    class_user_id = NumericProperty() 
    #last_lat = NumericProperty() 
    #last_lon = NumericProperty() 
    def build(self):
        try:
            self.root = MapViewBackground(orientation='vertical')
            gps.configure(on_location=self.on_location,on_status=self.on_status)
            who_respone = requests.get(who_url+"/%s"%plyer.uniqueid.id,"")
            self.class_user_id = who_respone.json()['iduser']
            if self.class_user_id == -1:
                make_response = requests.post(user_url+"/1/%s"%plyer.uniqueid.id,"")        
                status = make_response.json()['state']    
                if status == "FAIL" : 
                    self.class_user_id = 0
                who_respone = requests.get(who_url+"/%s"%plyer.uniqueid.id,"")
                self.class_user_id = who_respone.json()['iduser']

            self.mapview = self.root.ids.mv     
            self.mapview.center_on(37.3206023,127.1286901)
            layer = GeoJsonMapLayer(source="https://storage.googleapis.com/maps-devrel/google.json")
            self.mapview.add_layer(layer)
            inven_respone = requests.get(inven_url+"/%d/%s"%(self.class_user_id,plyer.uniqueid.id),"")
            self.mineral_cobble = inven_respone.json()[0]['cob']
            self.mineral_col = inven_respone.json()[0]['col']
            self.mineral_steel = inven_respone.json()[0]['steel']
            self.mineral_gold = inven_respone.json()[0]['gold']
            self.start(1000,0)
            self.mining_gauge = 0
            self.sensorEnabled = False            
            self.do_toggle()            
        except Exception as e:        
            self.error = "build" + str(e)
            
        return self.root
        
    def do_toggle(self):
        try:
            if not self.sensorEnabled:
                accelerometer.enable()
                Clock.schedule_interval(self.get_acceleration, 1 / 20.)
                self.sensorEnabled = True
                
            else:
                accelerometer.disable()
                Clock.unschedule(self.get_acceleration)

                self.sensorEnabled = False
                
        except Exception as e:        
            self.error = str(e) + "kmmm"    

    def get_acceleration(self, dt):
        try:
            val = accelerometer.acceleration[:3]

            if not val == (None, None, None):
                if not self.last_val == None:                                        
                    if abs(val[0] + val[1] + val[2] - self.last_val[0] - self.last_val[1] - self.last_val[2]) / ((1/20.) * 100) > GL_SHAKE_SCALE :                        
                        self.makemark()            
            self.last_val = val[:]
        except Exception as e:        
            self.last_val = val[:]
            self.error = str(e)
            
    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()
    
    def is_mine_dead(self, mine):
        try:
            if mine and (int(mine['hp']) is int(0)):
                return True
            else:
                return False 
        except Exception as e:
            self.error = str(e)
            return False
    beacon = None
    @mainthread
    def on_location(self, **kwargs):
        try:
            self.load_geo()
            if self.beacon: self.beacon.detach()
            self.gps_location = '\n'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])                
            self.mapview.center_on(kwargs.get('lat'),kwargs.get('lon'))
            self.beacon = Builder.load_string(whereami_loader%{"lat":kwargs.get('lat'),"lon":kwargs.get('lon')})
            #self.last_lat = kwargs.get('lat')
            #self.last_lon = kwargs.get('lon')
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
                    
                    if self.is_mine_dead(response_idmine.json()):
                        tmp = markerdic[i['idmine']]
                        self.mapview.remove_widget(tmp)
                        
                else:
                    
                    if not self.is_mine_dead(i):
                        user_id = requests.get(user_url+"/%s/%s"%(i['user'],plyer.uniqueid.id),"")
                        user_id = user_id.json()
                        _widget = Builder.load_string(marker_loader%{"lat":i['lat'],"lon":i['lon'],"source":user_id['team'],"hp":i['hp'], "team_name":user_id['team_name']})
                        self.mapview.add_widget(_widget)                        
                        markerdic[i['idmine']] = _widget
                        
            response = requests.get(api_url+"/%(lat)f/%(lon)f?around=%(distance)d"%{'lat':self.mapview.lat,'lon':self.mapview.lon,'distance':GL_MINE_DISTANCE},"")
            response = response.json()
            
            for i in response :                    
                if self.is_mine_dead(i):                     
                    response.remove(i)                    
            if response :
                self.is_am_i_in_mine = True
            else:
                self.is_am_i_in_mine = False            
            if self.mining_gauge <= 3 :
                self.mining_gauge = 0
            else:
                self.mining_gauge -= 3
            
        except Exception as e:                    
            self.error = "location" + str(e)
    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)
    def load_geo(self):
        try:
            respone = requests.get(geo_url,"")
            texts = geo_header
            for i in respone.json() :
                texts += geo_body%(team_color[i['idteam']],i['poly']) 
                
                
            texts = texts[:-1]
            texts += geo_footer
            jsons = json.loads(texts)
            layer = GeoJsonMapLayer(geojson=jsons)
            if self.old_layer:
                self.mapview.remove_layer(self.old_layer)
            self.mapview.add_layer(layer)
            self.old_layer = layer
        except Exception as e:                    
            self.error = "geo" +str(e)
        
    def makemark(self):
        try:
            
            if self.is_am_i_in_mine :                
                self.mining_gauge += 4
            else :
                self.mining_gauge += 2
                
            if self.mining_gauge >= 100 :
                
                self.mineral_cobble += 1
                self.mineral_col += 1
                self.mineral_steel += 1
                self.mineral_gold += 1
                self.mining_gauge = 0
                
                response = requests.put("http://build.ees.guru:8888/inven/%d/cob/%s?num=1"%(self.class_user_id,plyer.uniqueid.id),"")
                status = response.json()['state']
                if status == "FAIL" : 
                    return
                response = requests.put("http://build.ees.guru:8888/inven/%d/col/%s?num=1"%(self.class_user_id,plyer.uniqueid.id),"")
                status = response.json()['state']
                if status == "FAIL" : 
                    return
                response = requests.put("http://build.ees.guru:8888/inven/%d/steel/%s?num=1"%(self.class_user_id,plyer.uniqueid.id),"")
                status = response.json()['state']
                if status == "FAIL" : 
                    return
                response = requests.put("http://build.ees.guru:8888/inven/%d/gold/%s?num=1"%(self.class_user_id,plyer.uniqueid.id),"")
                status = response.json()['state']
                if status == "FAIL" : 
                    return
        except Exception as e:        
                self.error = str(e) 
    def makemark2(self):
        try:
            if (self.mineral_cobble >= GL_REQUIRE_COBBLE) and (self.mineral_col >= GL_REQUIRE_COL) and (self.mineral_steel >= GL_REQUIRE_STEEL) and (self.mineral_gold >= GL_REQUIRE_GOLD) :                        
                response = requests.get(api_url+"/%(lat)f/%(lon)f?around=50"%{'lat':self.mapview.lat,'lon':self.mapview.lon},"")
                response = response.json()
                for i in response :
                    
                    if self.is_mine_dead(i):                    
                        response.remove(i)
                if not response:
                    response2 = requests.post(api_url+"/%(lat)f/%(lon)f/%s"%{'lat':self.mapview.lat,'lon':self.mapview.lon},plyer.uniqueid.id,"")        
                    status = response2.json()['state']
                    if status == "FAIL" : 
                        return
                    user_id = requests.get(user_url+"/%d/%s"%(self.class_user_id,plyer.uniqueid.id),"")
                    user_id = user_id.json()
                    _widget = Builder.load_string(marker_loader%{"lat":self.mapview.lat,"lon":self.mapview.lon,"source":user_id['team'],"hp":1000, "team_name":user_id['team_name']})
                    self.mapview.add_widget(_widget)
                    markerdic[response2.json()['id']] = _widget
                    self.mineral_cobble -= GL_REQUIRE_COBBLE
                    self.mineral_col -= GL_REQUIRE_COL
                    self.mineral_steel -= GL_REQUIRE_STEEL
                    self.mineral_gold -= GL_REQUIRE_GOLD
                    response = requests.put("http://build.ees.guru:8888/inven/%d/cob/%s?num=-%d"%(self.class_user_id,plyer.uniqueid.id,GL_REQUIRE_COBBLE),"")
                    status = response.json()['state']
                    if status == "FAIL" : 
                        return
                    response = requests.put("http://build.ees.guru:8888/inven/%d/col/%s?num=-%d"%(self.class_user_id,plyer.uniqueid.id,GL_REQUIRE_COL),"")
                    status = response.json()['state']
                    if status == "FAIL" : 
                        return
                    response = requests.put("http://build.ees.guru:8888/inven/%d/steel/%s?num=-%d"%(self.class_user_id,plyer.uniqueid.id,GL_REQUIRE_STEEL),"")
                    status = response.json()['state']
                    if status == "FAIL" : 
                        return
                    response = requests.put("http://build.ees.guru:8888/inven/%d/gold/%s?num=-%d"%(self.class_user_id,plyer.uniqueid.id,GL_REQUIRE_GOLD),"")
                    status = response.json()['state']
                    if status == "FAIL" : 
                        return
                else :
                    self.root.popup.open()
            else :
                self.root.popup2.open()
        except Exception as e:        
                self.error = str(e) + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
                
MapViewApp().run()
