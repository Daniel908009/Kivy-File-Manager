from kivy.uix.actionbar import Label
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.filechooser import FileChooserIconView
from kivy.clock import Clock
import hashlib
import threading
import time
import os
import shutil
# getting the current directory
current_directory = os.getcwd()

# this is bit weird way to do this but here is a class that works as a thread handler
class ThreadHandler:
    def __init__(self):
        self.thread = threading.Thread(target=self.loadingThread)
        self.path = None
        self.caller = None
        self.running = True
        self.loaded = False
        self.all_selected_files = []
        self.thread.start()
    def loadingThread(self):
        while self.running:
            time.sleep(0.2)
            if self.path != None:
                p = self.path
                self.path = None
                self.selectRecursive(p)
                self.loaded = True
    def sendInfo(self, path, caller):
        self.path = path
        self.caller = caller
    def selectRecursive(self, path):
        time.sleep(0.001)
        if os.path.isdir(path):
            files = os.listdir(path) 
            for thing in files:
                self.selectRecursive(path + "/" + thing)
        else:
            if path not in self.all_selected_files:
                self.all_selected_files.append(path)
loadingThread = ThreadHandler()

# popup that is used for selecting files in the key word search screen, maybe will be enhanced to cover both screens in the future
class File_selecting_popup(Popup):
    
    def __init__(self, caller, filter_files, widget):
        super().__init__()
        self.caller = caller
        self.ids.filechooser.path = current_directory
        self.WidgetGiven = widget
        if filter_files != None:
            self.ids.filechooser.filters = [filter_files]

    def cancel(self):
        self.dismiss()

    def change_selector(self):
        if self.ids.selector.text == "Graphic":
            self.ids.filechooser_layout.clear_widgets()
            self.ids.filechooser_layout.add_widget(FileChooserIconView(path=current_directory))
        else:
            self.ids.filechooser_layout.clear_widgets()
            self.ids.filechooser_layout.add_widget(FileChooserListView(path=current_directory))
        
    def select(self, type):
        if self.ids.filechooser.selection == [] and type != "current":
            return
        if type == "selected":
            self.caller.ids.selected_files_title.text = "Selected Files"
            # getting the selected files
            selected_files = self.ids.filechooser.selection
            for file in selected_files:
                if file not in self.caller.all_selected_files:
                    loadingThread.sendInfo(file, self)
        elif type == "current":
            self.caller.ids.selected_files_title.text = "Selected Files"
            loadingThread.sendInfo(current_directory, self)
        self.widget = LoadingWidget(self.caller)
        Clock.schedule_interval(self.widget.textChange, 0.2)
        self.caller.ids.selected.add_widget(self.widget)
        self.caller.ids.selected.height += 70
        Clock.schedule_interval(self.checkLoading, 0.5)
        self.dismiss()
    def checkLoading(self, dt):
        if loadingThread.loaded:
            if len(loadingThread.all_selected_files) + len(self.caller.all_selected_files) < 30:
                self.caller.ids.selected.remove_widget(self.widget)
                self.caller.ids.selected.height -= 70
                Clock.unschedule(self.checkLoading)
                selected = loadingThread.all_selected_files
                loadingThread.all_selected_files = []
                loadingThread.loaded = False
                for file in selected:
                    self.addFile(file)
            else:
                self.caller.ids.selected.remove_widget(self.widget)
                self.caller.ids.selected.height -= 70
                Clock.unschedule(self.checkLoading)
                selected = loadingThread.all_selected_files
                for file in selected:
                    self.caller.all_selected_files.append(file)
                for widget in self.caller.ids.selected.children:
                    if widget != self.caller.ids.selected_files_title:
                        self.caller.ids.selected.remove_widget(widget)
                        self.caller.ids.selected.height -= 70
                self.caller.ids.selected.add_widget(OverFlowWidget(self.caller))
                self.caller.ids.selected.height += 100
                loadingThread.all_selected_files = []
                self.caller.ids.selected_files_title.text = "Selected Files"
    def addFile(self, path):
        name = path.split("/")[-1]
        file_widget = self.WidgetGiven(path, name, self.caller)
        self.caller.ids.selected.add_widget(file_widget)
        self.caller.all_selected_files.append(path)
        self.caller.ids.selected.height += 60

# widget used when a lot of files are selected
class OverFlowWidget(GridLayout):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.ids.name.text = "Too many files to display, selected " + str(len(self.caller.all_selected_files)) + " files"
    def remove_all(self):
        self.caller.ids.selected.clear_widgets()
        self.caller.all_selected_files = []
        self.caller.ids.selected.height = 70
        self.caller.ids.selected_files_title.text = "Selected files will be here"

# widget for the loading texts
class LoadingWidget(GridLayout):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.loadingTexts = ["|", "/", "-", "\\"]
    def textChange(self, dt):
        if self.ids.loadingSign.text == self.loadingTexts[-1]:
            self.ids.loadingSign.text = self.loadingTexts[0]
        self.ids.loadingSign.text = self.loadingTexts[self.loadingTexts.index(self.ids.loadingSign.text) + 1]

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
        self.caller.ids.selected.height -= 60
        if len(self.caller.all_selected_files) == 0:
            self.caller.ids.selected_files_title.text = "Selected files will be here"

# screen for searching keywords
class Key_Word_SearchScreen(Screen):

    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction='up')
        self.manager.transition.duration = 1.5
        self.manager.current = 'main'

    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'

    def find_duplicates_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'find_duplicates'

    def order_files(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'order_files'

    def rename_files_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'batch_renaming'

    def select_directories(self):
        popup = File_selecting_popup(self, None, FileWidget)
        popup.open()

    def search(self):
        keywords = self.ids.keyword.text.split(",")
        for k in keywords:
            keywords[keywords.index(k)] = k.strip()
        results = []
        if len(self.all_selected_files) > 0 and keywords != ['']:
            for file_path in self.all_selected_files:
                temp = 0
                if file_path.endswith(".png") or file_path.endswith(".jpg") or file_path.endswith(".jpeg") or file_path.endswith(".gif") or file_path.endswith(".bmp") or file_path.endswith(".tiff"):
                    pass
                else:
                    for keyword in keywords:
                        file = open(file_path, "r")
                        lines = file.readlines()
                        for line in lines:
                            for word in line.split(" "):
                                if keyword in word:
                                    temp += 1
                        file.close()
                name = file_path.split("/")[-1]
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
        if self.path.endswith(".png") or self.path.endswith(".jpg") or self.path.endswith(".jpeg") or self.path.endswith(".gif") or self.path.endswith(".bmp") or self.path.endswith(".tiff"):
            popup = ImageContentPopup(self.path)
        elif self.path.endswith(".mp4") or self.path.endswith(".avi") or self.path.endswith(".mkv") or self.path.endswith(".mov") or self.path.endswith(".flv") or self.path.endswith(".wmv"):
            pass # there will be no video player, because it is too complicated and not useful anyway
        else:
            popup = FileContentPopup(self.path)
        popup.open()

# popup for displaying the content of an image
class ImageContentPopup(Popup):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids.content.source = path

# popup for displaying the content of a file
class FileContentPopup(Popup):
    def __init__(self, path):
        super().__init__()
        self.path = path
        file = open(path, "r")
        lines = file.readlines()
        text = ""
        for line in lines:
            text += line
        file.close()
        self.ids.content.text = text
    def save(self):
        file = open(self.path, "w")
        file.write(self.ids.content.text)
        file.close()
        self.dismiss()

# screen for sorting files
class File_SortScreen(Screen):

    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction='up')
        self.manager.transition.duration = 1.5
        self.manager.current = 'main'

    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'

    def find_duplicates_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'find_duplicates'

    def order_files(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'order_files'

    def rename_files_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'batch_renaming'

    def select_directories(self):
        popup = File_selecting_popup(self, None, FileWidget)
        popup.open()

    def sort(self):
        if len(self.all_selected_files) > 0 and self.ids.sort_method.text != 'Select sorting method' and self.ids.original_files.text != 'Select action':
            if self.ids.sort_method.text == 'Sort by types':
                self.sort_by_types()
            elif self.ids.sort_method.text == 'Sort by size':
                self.sort_by_size_pop()
            elif self.ids.sort_method.text == 'Sort by date':
                self.sort_by_date_pop()
    
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
            if not os.path.exists(current_directory + "/" + type + "_files"):
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
                shutil.copy(file, current_directory + "/" + type + "_files/" + name)
    
    def sort_by_size_pop(self):
        # getting the size bariers
        self.size_bariers = []
        sizeBariersPop = SizeBariersPopup(self)
        sizeBariersPop.open()

    def sort_by_date_pop(self):
        self.date_bariers = []
        dateBariersPop = DateBariersPopup(self)
        dateBariersPop.open()
    
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
                        shutil.copy(file, current_directory + "/" + str(self.size_bariers[i]) + "-" + str(self.size_bariers[i + 1]) + "_files/" + name)
                if size >= self.size_bariers[-1]:
                    shutil.copy(file, current_directory + "/" + str(self.size_bariers[-1]) + "and_more_files/" + name)
        self.size_bariers = []
    def sort_by_date(self): # this is basically the same as the size sorting
        # adding zero to the date bariers in case it isnt there
        if 0 not in self.date_bariers:
            self.date_bariers.append(0)
        # reordering the date bariers
        self.date_bariers.sort()
        # creating directories for between the date bariers
        for i in range(len(self.date_bariers) - 1):
            os.mkdir(current_directory + "/" + str(self.date_bariers[i]) + "-" + str(self.date_bariers[i + 1]) + "_files")
        # adding the final directory for everything above the last date barier
        os.mkdir(current_directory + "/" + str(self.date_bariers[-1]) + "and_more_files")
        # moving the files to the directories or copying them, depends on the selected action
        if self.ids.original_files.text == 'Use original files':
            for file in self.all_selected_files:
                name = file.split('/')[-1]
                date = os.path.getmtime(file)
                date += 1970 * 31536000 # these additions are here because the date is in seconds since the first of january 1970
                date += 1 * 2592000
                date += 1 * 86400
                for i in range(len(self.date_bariers) - 1):
                    if date >= self.date_bariers[i] and date < self.date_bariers[i + 1]:
                        os.rename(file, current_directory + "/" + str(self.date_bariers[i]) + "-" + str(self.date_bariers[i + 1]) + "_files/" + name)
                if date >= self.date_bariers[-1]:
                    os.rename(file, current_directory + "/" + str(self.date_bariers[-1]) + "and_more_files/" + name)
        elif self.ids.original_files.text == 'Use copies':
            for file in self.all_selected_files:
                name = file.split('/')[-1]
                date = os.path.getmtime(file)
                date += 1970 * 31536000
                date += 1 * 2592000
                date += 1 * 86400
                for i in range(len(self.date_bariers) - 1):
                    if date >= self.date_bariers[i] and date < self.date_bariers[i + 1]:
                        shutil.copy(file, current_directory + "/" + str(self.date_bariers[i]) + "-" + str(self.date_bariers[i + 1]) + "_files/" + name)
                if date >= self.date_bariers[-1]:
                    shutil.copy(file, current_directory + "/" + str(self.date_bariers[-1]) + "and_more_files/" + name)
        self.date_bariers = []
        
# popup used for selecting date bariers
class DateBariersPopup(Popup):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.selected = []
    def add(self):
        self.ids.selected_files_title.text = "Selected Date Bariers"
        if self.ids.time.text != "" and self.ids.time.text not in self.selected and len(self.ids.time.text) >= 4:
            if int(self.ids.time.text[:4]) > 1970:
                self.ids.selected.add_widget(DateWidget(self.ids.time.text, self))
                self.ids.selected.height += 50
                self.ids.time.text = ""
    def select(self):
        if len(self.selected) > 0:
            for barier in self.selected:
                b = int(barier[:4]) * 31536000
                b+= int(barier[6:7]) * 2592000
                b+= int(barier[9:10]) * 86400
                b+= int(barier[12:13]) * 3600
                b+= int(barier[15:16]) * 60
                b+= int(barier[18:19])
                self.caller.date_bariers.append(b)
            self.caller.sort_by_date()
            self.dismiss()
    def textInput(self):
        if len(self.ids.time.text) > 14:
            self.ids.time.text = self.ids.time.text[:14]

# widget used in the date bariers popup
class DateWidget(GridLayout):
    def __init__(self, date, caller):
        super().__init__()
        text = date[:4]
        if len(date) > 5:
            text += "-" + date[4:6]
            if len(date) > 7:
                text += "-" + date[6:8]
                if len(date) > 9:
                    text += " " + date[8:10]
                    if len(date) > 11:
                        text += ":" + date[10:12]
                        if len(date) > 13:
                            text += ":" + date[12:]
                        else:
                            text += ":00"
                    else:
                        text += ":00:00"
                else:
                    text += " 00:00:00"
            else:
                text += "-01 00:00:00"
        else:
            text += "-01-01 00:00:00"
        self.ids.date.text = text
        self.caller = caller
        self.caller.selected.append(text)
    def remove(self):
        text = self.ids.date.text
        self.caller.ids.selected.remove_widget(self)
        self.caller.selected.remove(text)
        self.caller.ids.selected.height -= 50
        if len(self.caller.selected) == 0:
            self.caller.ids.selected_files_title.text = "Selected Date Bariers will be here"

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
            self.ids.selected.add_widget(SizeWidget(self.ids.size_barier.text, self))
            self.ids.selected.height += 50
            self.ids.size_barier.text = ""
    def select(self):
        if len(self.selected) > 0:
            for barier in self.selected:
                self.caller.size_bariers.append(int(barier))
            self.caller.sort_by_size()
            self.dismiss()

# widget used in the size bariers popup
class SizeWidget(GridLayout):
    def __init__(self, size, caller):
        super().__init__()
        self.ids.size.text = size
        self.caller = caller
    def remove(self):
        self.caller.ids.selected.remove_widget(self)
        self.caller.selected.remove(self.ids.size.text)
        self.caller.ids.selected.height -= 50
        if len(self.caller.selected) == 0:
            self.caller.ids.selected_files_title.text = "Selected Size Bariers will be here"

# main/opening screen
class MainScreen(Screen):

    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'

    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'

    def find_duplicates_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'find_duplicates'

    def order_files(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'order_files'

    def rename_files_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'batch_renaming'

# screen for finding duplicate files
class Find_DuplicatesScreen(Screen):

    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.transition.duration = 1.5
        self.manager.current = "main"
    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'
    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'
    def order_files(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'order_files'
    def rename_files_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'batch_renaming'

    def select_directories(self):
        popup = File_selecting_popup(self, None, FileWidget)
        popup.open()

    def search(self):
        if len(self.all_selected_files) > 0:
            results = []
            for file in self.all_selected_files:
                name = file.split("/")[-1]
                hash = hashlib.md5(open(file, "rb").read()).hexdigest()
                results.append([name, hash, file])
            duplicates = []
            ignore = []
            for result in results:
                temp = 1
                paths = [result[2]]
                for res in results:
                    if result != res:
                        if result[1] == res[1]:
                            if result[0] not in ignore and res[0] not in ignore:
                                temp += 1
                                ignore.append(result[0])
                                paths.append(res[2])
                if temp > 1:
                    duplicates.append([result[0], temp, result[1], paths])
            res_pop = DuplicatesResults(duplicates)
            res_pop.open()

# popup for displaying the results of the duplicate search
class DuplicatesResults(Popup):
    def __init__(self, results):
        super().__init__()
        self.ids.results_search.clear_widgets()
        if len(results) != 0:
            for result in results:
                result_widget = DuplicateSearchResultWidget(self, result[0], result[1], result[3][0], result[3]) # bit weird way to do it but it works
                self.ids.results_search.add_widget(result_widget)
                self.ids.results_search.height += 70
        else:
            self.ids.results_search.add_widget(Label(text="No duplicates found"))
            self.ids.results_search.height += 70

# widget used for displaying the results of the duplicate search and for giving the options of what to do with the duplicates
class DuplicateSearchResultWidget(GridLayout):
    def __init__(self, caller, name, number, path, paths):
        super().__init__()
        self.caller = caller
        self.ids.name.text = name
        self.ids.numberOfDuplicates.text = str(number)
        self.path = path
        self.paths = paths
    def show_file(self):
        if self.path.endswith(".png") or self.path.endswith(".jpg") or self.path.endswith(".jpeg") or self.path.endswith(".gif") or self.path.endswith(".bmp") or self.path.endswith(".tiff"):
            popup = ImageContentPopup(self.path)
        elif self.path.endswith(".mp4") or self.path.endswith(".avi") or self.path.endswith(".mkv") or self.path.endswith(".mov") or self.path.endswith(".flv") or self.path.endswith(".wmv"):
            pass
        else:
            popup = FileContentPopup(self.path)
        popup.open()
    def action(self):
        if self.ids.action.text == "Delete duplicates":
            for path in self.paths:
                try:
                    os.remove(path)
                    self.caller.ids.results_search.remove_widget(self)
                except:
                    pass
        else:
            self.caller.ids.results_search.remove_widget(self)

# screen with different ordering options, this is different from the sorting screen because this is not actually moving the files, it only displays them ordered, for example from largest to smallest file
class OrderFilesScreen(Screen):
    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.transition.duration = 1.5
        self.manager.current = "main"
    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'
    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'
    def find_duplicates_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'find_duplicates'
    def rename_files_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'batch_renaming'

    def select_directories(self):
        popup = File_selecting_popup(self, None, FileWidget)
        popup.open()
    
    def order(self):
        if len(self.all_selected_files) > 0 and self.ids.ascending.text != "Select order" and self.ids.order_by.text != "Select order":
            # saving the old list and clearing the screen
            old_list = []
            for file in self.ids.selected.children:
                if file != self.ids.selected_files_title:
                    old_list.append(file.path)
            temp = []
            for widget in self.ids.selected.children:
                if widget != self.ids.selected_files_title:
                    temp.append(widget)
            for widget in temp: # this has to be done in two seperate loops otherwise only half of the widgets would be removed
                self.ids.selected.remove_widget(widget)
                self.ids.selected.height -= 60
            # ordering the list of files
            if self.ids.order_by.text == "Size":
                self.order_by_size(old_list)
            elif self.ids.order_by.text == "Date":
                self.order_by_date(old_list)
            elif self.ids.order_by.text == "Name":
                self.order_by_name(old_list)

    def order_by_size(self, old_list):
        sizes = []
        for file in old_list:
            sizes.append([file, os.path.getsize(file)])
        sizes.sort(key=lambda x: x[1])
        if self.ids.ascending.text == "Descending":
            sizes.reverse()
        for size in sizes:
            file_widget = FileWidget(size[0], size[0].split("/")[-1], self)
            file_widget.ids.size.text = str(size[1]) + " bytes"
            self.ids.selected.add_widget(file_widget)
            self.ids.selected.height += 60
    def order_by_date(self, old_list):
        dates = []
        for file in old_list:
            dates.append([file, os.path.getmtime(file)])
        dates.sort(key=lambda x: x[1])
        if self.ids.ascending.text == "Descending":
            dates.reverse()
        for date in dates:
            file_widget = FileWidget(date[0], date[0].split("/")[-1], self)
            timeText = time.ctime(date[1])
            file_widget.ids.size.text = str(timeText)
            self.ids.selected.add_widget(file_widget)
            self.ids.selected.height += 60
    def order_by_name(self, old_list): # or in other words its sorted alphabetically
        names = []
        for file in old_list:
            names.append([file, file.split("/")[-1]])
        names.sort(key=lambda x: x[1])
        if self.ids.ascending.text == "Descending":
            names.reverse()
        for name in names:
            file_widget = FileWidget(name[0], name[0].split("/")[-1], self)
            self.ids.selected.add_widget(file_widget)
            self.ids.selected.height += 60

# class of the renaming window
class BatchRenamingScreen(Screen):
    def main_menu_screen(self):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.transition.duration = 1.5
        self.manager.current = "main"
    def find_keywords_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'key_word_search'
    def sort_files_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'file_sort'
    def find_duplicates_screen(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.transition.duration = 1.5
        self.manager.current = 'find_duplicates'
    def order_files(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.transition.duration = 1.5
        self.manager.current = 'order_files'
    
    def select_directories(self):
        popup = File_selecting_popup(self, None, RenamingWidget)
        popup.open()

    def rename(self):
        if len(self.all_selected_files) > 0 and self.ids.baseName.text != "" and self.ids.numbering.text != "Select method":
            if self.ids.numbering.text == "Using numbers":
                self.renameNumbers()
            elif self.ids.numbering.text == "Using letters":
                self.renameLetters()
            self.ids.baseName.text = ""
            self.ids.numbering.text = "Select method"
            self.all_selected_files = []
            widgettoremove = []
            for widget in self.ids.selected.children:
                if widget != self.ids.selected_files_title:
                    widgettoremove.append(widget)
            for widget in widgettoremove:
                self.ids.selected.remove_widget(widget)
                self.ids.selected.height -= 60

    def renameNumbers(self):
        name = self.ids.baseName.text
        number = 1
        for file in self.all_selected_files:
            extension = file.split("/")[-1].split(".")[-1]
            filesDirectory = file.split("/")[:-1]
            os.rename(file, "/".join(filesDirectory) + "/" + name + str(number) + "." + extension)
            number += 1

    def renameLetters(self):
        alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"] # there is probably some way of making this less weird, but this works
        name = self.ids.baseName.text
        number = 0
        baseText = "-"
        for file in self.all_selected_files:
            extension = file.split("/")[-1].split(".")[-1]
            filesDirectory = file.split("/")[:-1]
            if number == 26:
                number = 0
                baseText += alphabet[number]
            os.rename(file, "/".join(filesDirectory) + "/" + name + baseText + alphabet[number] + "." + extension)
            number += 1

# renaming widget is basicaly file widget but with two extra buttons for changing the order of the files
class RenamingWidget(GridLayout):
    def __init__(self, path, name, caller):
        super().__init__()
        self.ids.name.text = name
        self.path = path
        self.caller = caller
    def moveUp(self):
        index = self.caller.all_selected_files.index(self.path)
        if index - 1 >= 0:
            self.caller.all_selected_files = []
            widgetstoremove = []
            for widget in self.caller.ids.selected.children:
                if widget != self.caller.ids.selected_files_title:
                    self.caller.all_selected_files.append(widget.path)
                    widgetstoremove.append(widget)
            self.caller.all_selected_files = reversed(self.caller.all_selected_files)
            for widget in widgetstoremove: # this has to be a seperate loop because otherwise the list would change while iterating which is no good
                self.caller.ids.selected.remove_widget(widget)
                self.caller.ids.selected.height -= 60
            temp = self.caller.all_selected_files[index - 1]
            self.caller.all_selected_files[index - 1] = self.caller.all_selected_files[index]
            self.caller.all_selected_files[index] = temp
            
            for file in self.caller.all_selected_files:
                name = file.split("/")[-1]
                file_widget = RenamingWidget(file, name, self.caller)
                self.caller.ids.selected.add_widget(file_widget)
                self.caller.ids.selected.height += 60
    def moveDown(self):
        index = self.caller.all_selected_files.index(self.path)
        if index + 1 < len(self.caller.all_selected_files):
            self.caller.all_selected_files = []
            widgetstoremove = []
            for widget in self.caller.ids.selected.children:
                if widget != self.caller.ids.selected_files_title:
                    self.caller.all_selected_files.append(widget.path)
                    widgetstoremove.append(widget)
            self.caller.all_selected_files = reversed(self.caller.all_selected_files)
            for widget in widgetstoremove:
                self.caller.ids.selected.remove_widget(widget)
                self.caller.ids.selected.height -= 60
            temp = self.caller.all_selected_files[index + 1]
            self.caller.all_selected_files[index + 1] = self.caller.all_selected_files[index]
            self.caller.all_selected_files[index] = temp
            for file in self.caller.all_selected_files:
                name = file.split("/")[-1]
                file_widget = RenamingWidget(file, name, self.caller)
                self.caller.ids.selected.add_widget(file_widget)
                self.caller.ids.selected.height += 60

# app class with the screen manager
class File_ManagerApp(App):

    def build(self):
        # this block of code is the switch screen manager setup
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(Key_Word_SearchScreen(name='key_word_search'))
        sm.add_widget(File_SortScreen(name='file_sort'))
        sm.add_widget(Find_DuplicatesScreen(name='find_duplicates'))
        sm.add_widget(OrderFilesScreen(name='order_files'))
        sm.add_widget(BatchRenamingScreen(name='batch_renaming'))
        return sm
    
# running the app
if __name__ == "__main__":
    File_ManagerApp().run()

loadingThread.running = False