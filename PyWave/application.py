""" This file contains the top level application definition.

There should only ever be one instance of the Application class,
it is however designed to work with multiple instances.
"""

import os

import wx
import yaml
import pygame

from .projects import Project
from .event_manager import EventManager
from .structures import ShowError

#--------------------------------------------------------
#                       Constants
#--------------------------------------------------------

WINDOW_TITLE = "PyWave"
MIN_WINDOW_SIZE = (800, 580)
ICON_PATH = "Data/icon.ico"
SAVE_FILE = "main.prefs"

#--------------------------------------------------------
#                       Application
#--------------------------------------------------------

class Application(wx.Frame):
    """PyWave Application class.

    Inherits from wx.Frame but uses wx.App,
    to run like an application.
    """

    #-------------------------------------------
    #              Setup Methods
    #-------------------------------------------

    def __init__(self):
        #Make application instance
        self.app = wx.App(redirect=False)

        #Initialize the frame
        wx.Frame.__init__(self, None)

        #Set window properties
        self.SetMinSize(MIN_WINDOW_SIZE)
        self.SetTitle(WINDOW_TITLE)
        self.SetIcon(wx.Icon(ICON_PATH, wx.BITMAP_TYPE_ICO))

        #Bind Window close event
        self.Bind(wx.EVT_CLOSE, self._OnClose)

        #Make window subsystems
        self._make_menus()

        #Make sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        #Make event handler
        self.events = EventManager()

        #Make project
        self.project = None
        self._set_project(Project(self))

    def _make_menus(self):
        """ Setup the menu items for the application.
        """

        #Make a new MenuBar
        menu_bar = wx.MenuBar()

        #Setup menus
        menus = {
            "&File": [
                ["New Project", self._OnNew, wx.ID_NEW, "Ctrl+N"],
                ["Open Project", self._OnOpen, wx.ID_OPEN, "Ctrl+O"],
                ["Save Project", self._OnSave, wx.ID_SAVE, "Ctrl+S"],
                ["Save Project As...", self._OnSaveAs,
                 wx.ID_SAVEAS, "CTRL+Shift+S"],
                None, #--separator
                ["Quit", self._OnClose, wx.ID_EXIT, "Alt+F4"],
            ],
            "&Edit": [
                ["Undo", self._OnUndo, wx.ID_UNDO, "Ctrl+Z"],
                ["Redo", self._OnRedo, wx.ID_REDO, "Ctrl+Shift+Z"],
            ],
        }

        #Make menus
        for name in menus:
            #Make a new menu
            menu = wx.Menu()
            for item in menus[name]:
                #Handle Separators
                if not item:
                    menu.AppendSeparator()
                    continue

                #Add menu item: id, name + shortcut
                menu_item = menu.Append(item[2], item[0] + "\t" + item[3])

                #Bind menu item
                self.Bind(wx.EVT_MENU, item[1], menu_item)

            #Add menu to menu-bar
            menu_bar.Append(menu, name)

        #Set the menu-bar of the application
        self.SetMenuBar(menu_bar)

    #-------------------------------------------
    #             Runtime Methods
    #-------------------------------------------

    def run(self, target_path):
        """ Run the Application.
        """
        #Initialize pygame's sound system
        pygame.mixer.init(buffer=1024)
        #Show the application
        self._load_prefs()
        self.Show()

        #Load the targeted project if possible
        if target_path is not None:
            self._open_project(target_path)

        #Run the application
        self.app.MainLoop()

    def _open_project(self, path, err_for_fail=True):
        """ Loads a project from a path, handling errors.

        if err_for_fail is set to False, errors are passed silently.
        """
        #Test if path exists
        if not os.path.isfile(path) and err_for_fail:
            ShowError(self, "File Error", "%s is not a valid file path" % path)

        try:
            #Get project data
            with open(path, "r") as _file:
                data = yaml.load(_file.read())

            #Make new project
            new = Project(self)
            #Set it's save path
            new.save_path = path
            #Deserialize the data
            new.deserialize(data)

            #Cleanup
            self.project.Destroy()
            #Set the applications project
            self._set_project(new)
        except Exception:
            if err_for_fail:
                ShowError(self, "File load Error",
                          "Error opening requested file")

    def _set_project(self, project):
        """ Set the project the application uses.

        This is required due to the event and GUI system.
        """
        self.project = project
        #Event System
        self.events.reset()
        #GUI
        self.sizer.Add(project, 1, wx.EXPAND)
        self.Layout()

    def _save_prefs(self):
        """ Save the application's preferences to the SAVE_FILE.
        """
        data = {
            "size" : self.GetSize(),
            "pos" : self.GetPosition(),
            "max" : self.IsMaximized(),
            "open" : self.project.save_path,
        }
        #Get savefile
        with open(SAVE_FILE, "w") as _file:
            dump = yaml.dump(data)
            _file.write(dump)

    def _load_prefs(self):
        """ Load the application's preferences from the SAVE_FILE.
        """
        if not os.path.exists(SAVE_FILE):
            return

        #Ignore any errors for preference loading
        try:
            #Load YAML data
            with open(SAVE_FILE, "r") as _file:
                data = yaml.load(_file.read())

            #Set the window preferences
            self.SetSize(data["size"])
            self.SetPosition(data["pos"])
            if data["max"]:
                self.Maximize()

            #Load previously opened file
            if data["open"]:
                if os.path.exists(data["open"]):
                    self._open_project(data["open"], False)
        except Exception:
            pass

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def _OnNew(self, event):
        """ Event called when Ctrl+N, or File/New is pressed.

        Creates a new, empty project,
        after some checks with the current project.
        """

        #Close the current project
        if self.project.close():
            #On cancel, return
            return

        #Destroy the current project
        self.project.Destroy()
        #Set the current project to a new, empty project
        self._set_project(Project(self))

    def _OnOpen(self, event):
        """ Event called when Ctrl-O, or File/Open is pressed.

        Loads a project from a filepath given by the user,
        after closing the current project.
        """
        #Close the current project
        if self.project.close():
            return

        #Get a new filepath to a project from the user
        dialog = wx.FileDialog(self, "Open Project File", "", "",
                               "Project File (*.pywave)|*.pywave",
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        status = dialog.ShowModal()
        #Return for cancels
        if status == wx.ID_CANCEL:
            return

        #Get the selected path
        path = dialog.GetPath()

        #Load the new project from file
        self._open_project(path)

    def _OnSave(self, event):
        """ Event called by Ctrl+S, or when File/Save is pressed.

        Saves the project to file. If the project has not previously been saved,
        the user is asked for a savepath.
        """
        self.project.save()

    def _OnSaveAs(self, event):
        """ Event called by Ctrl+Shift+S, or when File/Save As... is pressed.

        Asks the user for a filepath and saves the current project to that path.
        """
        self.project.save_as()

    def _OnUndo(self, event):
        """ Event called by Ctrl+Z, or when Edit/Undo is pressed.

        Undoes one user event.
        """
        self.events.undo()

    def _OnRedo(self, event):
        """ Event called by Ctrl+Shift+Z or when Edit/Redo is pressed.

        Redoes one undid user event.
        """
        self.events.redo()

    def _OnClose(self, event):
        """ Event called when the application is being or should be closed.
        """
        #Close the project
        if self.project.close():
            #Veto application closing on "cancel"
            if hasattr(event, "Veto"):
                event.Veto()
            return

        #Save application settings
        self._save_prefs()

        #Close the window
        self.Destroy()
