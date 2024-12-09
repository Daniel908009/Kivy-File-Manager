from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.popup import Popup
import os
# getting the current directory
current_directory = os.getcwd()

class File_selecting_popup(Popup):
    def send_info(self, caller):
        self.caller = caller
        self.ids.filechooser.path = current_directory
    def cancel(self):
        self.dismiss()
    def select(self):
        #print("Selected")
        # getting the selected files
        selected_files = self.ids.filechooser.selection
        #print(selected_files)
        for file in selected_files:
            name = file.split("/")[-1]
            path = file
            if path not in self.caller.all_selected_files:
                if os.path.isdir(path):
                    #print("Directory")
                    files = os.listdir(path)
                    #print(files)
                    for thing in files:
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
        #print(self.caller.all_selected_files)
        self.dismiss()

class FileWidget(GridLayout):
    def set_info(self, path, name, caller):
        self.ids.name.text = name
        self.path = path
        self.caller = caller
    def remove_file(self):
        self.caller.ids.selected.remove_widget(self)
        self.caller.all_selected_files.remove(self.path)
        self.caller.ids.selected.height -= 70

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
        self.ids.keyword.text = ""
        results = []
        if keyword != "":
            temp = 0
            for file in self.all_selected_files:
                file = open(file, "r")
                lines = file.readlines()
                for line in lines:
                    if keyword in line:
                        #print(file.name)
                        temp += 1
                file.close()
                #print("Total number of keyword in file "+ file.name + ": ", temp)
                name = file.name.split("/")[-1]
                results.append([name, temp])
                temp = 0
            print(results)
            res_pop = KeyWordsResults()
            res_pop.send_info(results)
            res_pop.open()
        else:
            pass

class KeyWordsResults(Popup):
    def send_info(self, results):
        self.ids.results_search.clear_widgets()
        for result in results:
            result_widget = ResultWidget()
            result_widget.set_info(result[0], result[1])
            self.ids.results_search.add_widget(result_widget)

class ResultWidget(GridLayout):
    def set_info(self, name, count):
        self.ids.name.text = name
        self.ids.count.text = str(count)

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

class MainScreen(Screen):
    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'
    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'

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