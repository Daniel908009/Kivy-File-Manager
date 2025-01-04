from kivy.uix.actionbar import Label
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.popup import Popup
import os
# getting the current directory
current_directory = os.getcwd()

# popup that is used for selecting files in the key word search screen, maybe will be enhanced to cover both screens in the future
class File_selecting_popup(Popup):
    
    def __init__(self, caller, filter_files):
        super().__init__()
        self.caller = caller
        self.ids.filechooser.path = current_directory
        if filter_files != None:
            self.ids.filechooser.filters = [filter_files]

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
                            file_widget = FileWidget(path + "/" + thing, thing, self.caller)
                            self.caller.ids.selected.add_widget(file_widget)
                            self.caller.all_selected_files.append(path + "/" + thing)
                            self.caller.ids.selected.height += 70
                else:    
                    file_widget = FileWidget(path, name, self.caller)
                    self.caller.ids.selected.add_widget(file_widget)
                    self.caller.all_selected_files.append(file)
                    self.caller.ids.selected.height += 70
        self.dismiss()

# widget for displaying selected files in the scroll view
class FileWidget(GridLayout):

    def __init__(self, path, name, caller):
        super().__init__()
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
        popup = File_selecting_popup(self, None)
        popup.open()

    def search(self):
        keywords = self.ids.keyword.text.split(",")
        for k in keywords:
            keywords[keywords.index(k)] = k.strip()
        results = []
        #print(keywords)
        if len(self.all_selected_files) > 0 and keywords != ['']:
            for file_path in self.all_selected_files:
                temp = 0
                for keyword in keywords:
                    file = open(file_path, "r")
                    lines = file.readlines()
                    for line in lines:
                        for word in line.split(" "):
                            if keyword in word:
                                temp += 1
                    file.close()
                name = file.name.split("/")[-1]
                results.append([name, temp])
            res_pop = KeyWordsResults(results, self.all_selected_files)
            res_pop.open()

# popup for displaying the results of the keyword search
class KeyWordsResults(Popup):

    def __init__(self, results, paths):
        super().__init__()
        self.ids.results_search.clear_widgets()
        self.paths = paths
        for result in results:
            result_widget = ResultWidget(result[0], result[1], self.paths[results.index(result)])
            self.ids.results_search.add_widget(result_widget)
            self.ids.results_search.height += 70

# widget for displaying the results of the keyword search inside the results popup
class ResultWidget(GridLayout):

    def __init__(self, name, count, path):
        super().__init__()
        self.ids.name.text = name
        self.ids.count.text = str(count)
        self.path = path
        if count > 0:
            self.ids.count.color = 0, 1, 0, 1
            self.ids.name.color = 0, 1, 0, 1
    def show_file(self):
        popup = FileContentPopup(self.path)
        popup.open()

# popup for displaying the content of a file
class FileContentPopup(Popup):
    def __init__(self, path):
        super().__init__()
        file = open(path, "r")
        lines = file.readlines()
        text = ""
        for line in lines:
            text += line
        file.close()
        self.ids.content.text = text

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
        popup = File_selecting_popup(self, None)
        popup.open()

    def sort(self):
        if len(self.all_selected_files) > 0 and self.ids.sort_method.text != 'Select sorting method' and self.ids.original_files.text != 'Select action':
            if self.ids.sort_method.text == 'Sort by types':
                self.sort_by_types()
            elif self.ids.sort_method.text == 'Sort by size':
                self.sort_by_size_pop()
            elif self.ids.sort_method.text == 'Sort by date':
                self.sort_by_date()
    
    def sort_by_types(self):
        # getting all the types of the selected files
        types = []
        for file in self.all_selected_files:
            name = file.split("/")[-1]
            if "." in name:
                type = name.split(".")[-1]
                if type not in types:
                    types.append(type)
        # creating directories for each type
        for type in types:
            os.mkdir(current_directory + "/" + type + "_files")
        # moving the files to the directories or copying them, depends on the selected action
        if self.ids.original_files.text == 'Use original files':
            for file in self.all_selected_files:
                name = file.split("/")[-1]
                type = name.split(".")[-1]
                os.rename(file, current_directory + "/" + type + "_files/" + name)
        elif self.ids.original_files.text == 'Use copies':
            for file in self.all_selected_files:
                name = file.split("/")[-1]
                type = name.split(".")[-1]
                os.system("cp " + file + " " + current_directory + "/" + type + "_files/" + name)
    
    def sort_by_size_pop(self):
        # getting the size bariers
        self.size_bariers = []
        sizeBariersPop = SizeBariersPopup(self)
        sizeBariersPop.open()

    def sort_by_date(self):
        pass # will be implemented later
    
    def sort_by_size(self):
        # adding zero to the size bariers in case it isnt there
        if 0 not in self.size_bariers:
            self.size_bariers.append(0)
        # reordering the size bariers
        self.size_bariers.sort()
        # creating directories for between the size bariers
        for i in range(len(self.size_bariers) - 1):
            os.mkdir(current_directory + "/" + str(self.size_bariers[i]) + "-" + str(self.size_bariers[i + 1]) + "_files")
        # adding the final directory for everything above the last size barier
        os.mkdir(current_directory + "/" + str(self.size_bariers[-1]) + "and_more_files")
        # moving the files to the directories or copying them, depends on the selected action
        if self.ids.original_files.text == 'Use original files':
            for file in self.all_selected_files:
                name = file.split('/')[-1]
                size = os.path.getsize(file)
                for i in range(len(self.size_bariers) - 1):
                    if size >= self.size_bariers[i] and size < self.size_bariers[i + 1]:
                        os.rename(file, current_directory + "/" + str(self.size_bariers[i]) + "-" + str(self.size_bariers[i + 1]) + "_files/" + name)
                if size >= self.size_bariers[-1]:
                    os.rename(file, current_directory + "/" + str(self.size_bariers[-1]) + "and_more_files/" + name)
        elif self.ids.original_files.text == 'Use copies':
            for file in self.all_selected_files:
                name = file.split('/')[-1]
                size = os.path.getsize(file)
                for i in range(len(self.size_bariers) - 1):
                    if size >= self.size_bariers[i] and size < self.size_bariers[i + 1]:
                        os.system("cp " + file + " " + current_directory + "/" + str(self.size_bariers[i]) + "-" + str(self.size_bariers[i + 1]) + "_files/" + name)
                if size >= self.size_bariers[-1]:
                    os.system("cp " + file + " " + current_directory + "/" + str(self.size_bariers[-1]) + "and_more_files/" + name)

# popup used for selecting size bariers
class SizeBariersPopup(Popup):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
    def cancel(self):
        self.dismiss()
    def add(self):
        self.ids.selected_files_title.text = "Selected Size Bariers"
        if self.ids.size_barier.text != "" and self.ids.size_barier.text not in self.selected:
            self.selected.append(self.ids.size_barier.text)
            self.ids.selected.add_widget(Label(text=self.ids.size_barier.text, height=70, font_size=20)) # later will be widget
            self.ids.selected.height += 70
            self.ids.size_barier.text = ""
    def select(self):
        for barier in self.selected:
            self.caller.size_bariers.append(int(barier))
        self.caller.sort_by_size()
        self.dismiss()

# main/opening screen
class MainScreen(Screen):

    def get_joke(self): # this is will be done later
        pass

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
        # this block of code is the switch screen manager setup
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(Key_Word_SearchScreen(name='key_word_search'))
        sm.add_widget(File_SortScreen(name='file_sort'))

        return sm
    
# running the app
if __name__ == "__main__":
    File_ManagerApp().run()