from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.popup import Popup
import os
# getting the current directory
current_directory = os.getcwd()

# popup that is used for selecting files in the key word search screen, maybe will be enhanced to cover both screens in the future
class File_selecting_popup(Popup):
    
    def send_info(self, caller):
        self.caller = caller
        self.ids.filechooser.path = current_directory

    def cancel(self):
        self.dismiss()

    def select(self):
        self.caller.ids.selected_files_title.text = "Selected Files"
        # getting the selected files
        selected_files = self.ids.filechooser.selection
        for file in selected_files:
            name = file.split("/")[-1]
            path = file
            if path not in self.caller.all_selected_files:
                if os.path.isdir(path):
                    files = os.listdir(path) 
                    for thing in files:
                        if os.path.isfile(path + "/" + thing): # directories inside directories will for now be ignored maybe in the future I will figure out some way to add a system for that
                            file_widget = FileWidget()
                            file_widget.set_info(path + "/" + thing, thing, self.caller)
                            self.caller.ids.selected.add_widget(file_widget)
                            self.caller.all_selected_files.append(path + "/" + thing)
                            self.caller.ids.selected.height += 70
                else:    
                    file_widget = FileWidget()
                    file_widget.set_info(path, name, self.caller)
                    self.caller.ids.selected.add_widget(file_widget)
                    self.caller.all_selected_files.append(file)
                    self.caller.ids.selected.height += 70
        self.dismiss()

# widget for displaying selected files in the scroll view
class FileWidget(GridLayout):

    def set_info(self, path, name, caller):
        self.ids.name.text = name
        self.path = path
        self.caller = caller

    def remove_file(self):
        self.caller.ids.selected.remove_widget(self)
        self.caller.all_selected_files.remove(self.path)
        self.caller.ids.selected.height -= 70
        if len(self.caller.all_selected_files) == 0:
            self.caller.ids.selected_files_title.text = "Selected files will be here"

# screen for searching keywords
class Key_Word_SearchScreen(Screen):

    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'main'

    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'

    def select_directories(self):
        popup = File_selecting_popup()
        popup.send_info(self)
        popup.open()

    def search(self):
        keyword = self.ids.keyword.text
        results = []
        if keyword != "" and len(self.all_selected_files) > 0:
            temp = 0
            for file_path in self.all_selected_files:
                file = open(file_path, "r")
                lines = file.readlines()
                for line in lines:
                    if keyword in line:
                        temp += 1
                file.close()
                name = file.name.split("/")[-1]
                results.append([name, temp])
                temp = 0
            res_pop = KeyWordsResults()
            res_pop.send_info(results)
            res_pop.open()
        else:
            pass

# popup for displaying the results of the keyword search
class KeyWordsResults(Popup):

    def send_info(self, results):
        self.ids.results_search.clear_widgets()
        for result in results:
            result_widget = ResultWidget()
            result_widget.set_info(result[0], result[1])
            self.ids.results_search.add_widget(result_widget)
            self.ids.results_search.height += 70

# widget for displaying the results of the keyword search inside the results popup
class ResultWidget(GridLayout):

    def set_info(self, name, count):
        self.ids.name.text = name
        self.ids.count.text = str(count)
        if count > 0:
            self.ids.count.color = 0, 1, 0, 1
            self.ids.name.color = 0, 1, 0, 1

# screen for sorting files
class File_SortScreen(Screen):

    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'main'

    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'

    def select_directories(self):
        popup = File_selecting_popup()
        popup.open()

# main/opening screen
class MainScreen(Screen):

    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'

    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'

# app class with the screen manager
class File_ManagerApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(Key_Word_SearchScreen(name='key_word_search'))
        sm.add_widget(File_SortScreen(name='file_sort'))
        return sm
    
# running the app
if __name__ == "__main__":
    File_ManagerApp().run()