# Author: B&B
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.vkeyboard import VKeyboard
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from functools import partial
from kivy.config import Config
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy import require

# This example uses features introduced in Kivy 1.8.0, namely being able to load
# custom json files from the app folder
require("1.8.0")
Builder.load_file('FriendsScreen.kv')
Builder.load_file('MainScreen.kv')
Builder.load_file('GameStartScreen.kv')
Builder.load_file('MyinfoScreen.kv')
		
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

    def build(self):
        self.sm = ScreenManager()        
        self.sm.add_widget(MainScreen(name="MainScreen"))
        self.sm.add_widget(FriendsScreen(name="FriendsScreen"))
        self.sm.add_widget(GameStartScreen(name="GameStartScreen"))
        self.sm.add_widget(MyinfoScreen(name="MyinfoScreen"))
        self.sm.current = "MainScreen"
        return self.sm

if __name__ == "__main__":
    TestDemo().run()

	