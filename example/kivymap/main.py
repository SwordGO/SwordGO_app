from mapview import MapView
from mapview import MapMarkerPopup
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, \
    AliasProperty, BooleanProperty, StringProperty
from os.path import join, dirname
from kivy.lang import Builder
from kivy.uix.bubble import Bubble
class MapMark(MapMarkerPopup):
    pass
    
marker_loader = '''
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
    
class MapViewApp(App):
    def build(self):
        mapview = MapView(zoom=11, lat=50.6394, lon=3.057)
        
        b=MapMark(lat=50.6494,lon=3.057,popup_size= (dp(230), dp(130)),source = "icons/marker2.png")
        #b.add_widget(bubble())
        c=MapMark(lat=50.6294,lon=3.057,popup_size= (dp(230), dp(130)),source = "icons/marker3.png")
        d = Builder.load_string(marker_loader%{"lat":50.6194,"lon":3.057,"source":1})
        mapview.add_widget(d)
        mapview.add_widget(MapMark(lat=50.6394,lon=3.057,popup_size= (dp(230), dp(130)),source ="icons/marker1.png" ))
        mapview.add_widget(b)
        mapview.add_widget(c)
        return mapview

MapViewApp().run()
