from kivy.app import App
from kivy.uix.widget import Widget
 
class OSXGuiWidget(Widget):
    pass
 
class OSXGuiApp(App):
    def build(self):
        return OSXGuiWidget()
    
class RootWidget(App):
    def build(self):
        return RootWidget() 
 
if __name__ == '__main__':
    OSXGuiApp().run()
    RootWidget().run()
