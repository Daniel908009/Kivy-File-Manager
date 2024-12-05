from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView









class Key_Word_SearchScreen(Screen):
    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'main'
    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'

class File_SortScreen(Screen):
    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'main'
    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'


class MainScreen(Screen):
    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'
    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'

class File_ManagerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(Key_Word_SearchScreen(name='key_word_search'))
        sm.add_widget(File_SortScreen(name='file_sort'))
        return sm
    
if __name__ == "__main__":
    File_ManagerApp().run()