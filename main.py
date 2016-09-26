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
Builder.load_string('''
<PressedScreen>:
	
	BoxLayout:

		orientation: 'vertical'
		padding: 20
		spacing: 100
		Button:
			text: "Game Start"
			pos_hint: {'x':.25, 'y': 0.5}		
			size_hint: 0.5, 0.5
		Button:
			text: "My info"
			pos_hint: {'x':0.4, 'y': 0.1}
			size_hint: 0.2, 0.1
		Button:
			text: "Friends"
			pos_hint: {'x':0.4, 'y': 0.1}
			size_hint: 0.2, 0.1
			on_release: root.manager.current = "mode"
			
<FirstScreen>:	
	FloatLayout:	

		Button:
			text: "Button 3"
			pos_hint: {'x': .8, 'y': .6}
			size_hint: .2, .2
			on_release: root.next()

''')

		
class FirstScreen(Screen):
	def next(self):
		self.manager.current = "MainScreen"


class PressedScreen(Screen):
	def __init__(self, **kwargs):
		super(PressedScreen, self).__init__(**kwargs)
        

class TestDemo(App):
    sm = None  # The root screen manager

    def build(self):
        self.sm = ScreenManager()        
        self.sm.add_widget(PressedScreen(name="MainScreen"))
        self.sm.add_widget(FirstScreen(name="mode"))
        self.sm.current = "MainScreen"
        return self.sm

if __name__ == "__main__":
    TestDemo().run()
