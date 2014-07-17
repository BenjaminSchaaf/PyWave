""" This file includes definitions for the base Project structure.

Since the Master structure is too small for it's own file, it is also
located along with the Project structure.
"""

import os

import wx
import yaml

from .sounds import Sounds
from .mixers import Mixers
from .cues import CuesEditor
from .structures import Tab

#--------------------------------------------------------
#                       Constants
#--------------------------------------------------------

#The notice to go along with saved files, just in case people are dump
FILENOTICE = """
##==================NOTICE==================##
# This is a auto-generated PyWave save file. #
# Editing this file is dangerous and might   #
# cause problems with PyWave.                #
# Unless you know what you're going, please  #
# DO NOT TOUCH THIS FILE!                    #
##==================NOTICE==================##

"""

#--------------------------------------------------------
#                        Project
#--------------------------------------------------------

class Project(wx.Panel):
    """ This class defines a single Project, made of Sounds, Mixers and their
    Cues, as well as all UI functions.
    """
    def __init__(self, application):
        wx.Panel.__init__(self, application)
        #Set properties
        self.application = application
        self.save_path = None
        self.editing = None

        #Make sizers
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        #Add Master area on the left
        self.master = Master(self)
        self.sizer.Add(Tab(self, self.master, "Master"), 1, wx.EXPAND)

        #Add Mixers area in the middle
        self.mixers = Mixers(self)
        self.mixers_tab = Tab(self, self.mixers, "Mixers")
        self.sizer.Add(self.mixers_tab, 9, wx.EXPAND)

        #Add Sounds area on the right
        self.sounds = Sounds(self)
        self.sizer.Add(Tab(self, self.sounds, "Sounds"), 4, wx.EXPAND)

        #Make Cue editor, but don't add it to sizer
        self.cues = CuesEditor(self)
        self.cues_tab = Tab(self, self.cues, "Cues")
        self.cues_tab.Hide()

    def close(self):
        """ Closes the project, with possible closing dialoges.

        Determines whether the project needs to be saved.
        Returns True when closing has been canceled, otherwise False.
        """
        if self.save_path:
            #Check whether the already saved project is equivalent
            with open(self.save_path, "r") as _file:
                #If it is, we don't care
                if yaml.load(_file) == self.serialize():
                    return False

        #Check for empty project
        elif not self.mixers.mixers and not self.sounds.sounds:
            return False

        #Ask whether we want to save or not
        dialog = wx.MessageDialog(None, 'Save the project?', 'Before you go!',
                                  wx.YES_NO | wx.NO_DEFAULT |
                                  wx.CANCEL | wx.ICON_QUESTION)
        #Act accordingly
        status = dialog.ShowModal()
        #Exit cases
        if status == wx.ID_CANCEL:
            return True
        elif status == wx.ID_NO:
            return False

        #Save, otherwise
        self.save()
        return False

    def save(self):
        """ Save the project to file.

        If the project is not linked to a file, save_as is used instead.
        Otherwise, the project is YAML dumped to file.
        """
        #Check if we are associated to a file
        if not self.save_path:
            self.save_as()
            return

        #Save to file with a YAML dump
        data = self.serialize()
        with open(self.save_path, "w") as _file:
            lines = yaml.dump(data, default_flow_style=False)
            #prepend the file notice
            _file.write(FILENOTICE + lines)

    def save_as(self):
        """ Ask where to save the project and then save it.

        Calls save once the path has been determined.
        """
        dialog = wx.FileDialog(self, "Save Project File", "", "",
                               "Project File (*.pywave)|*.pywave",
                               wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        #Exit conditions
        status = dialog.ShowModal()
        if status == wx.ID_CANCEL:
            return
        #Get the selected path
        path = dialog.GetPath()
        #Make sure we have a .pywave extension
        name, ext = os.path.splitext(path)
        if ext != ".pywave":
            path = name + ".pywave"
        #Set the save path and save
        self.save_path = path
        self.save()

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnEdit(self, mixer):
        """ OnEdit is called when a mixer enters edit mode.

        Hides the mixers area and replaces it with the cues editor.
        Also set's up the cues editor for the selected mixer.
        """
        #Set editing mixer
        self.editing = mixer

        #Mide mixers area
        self.mixers_tab.Hide()
        self.sizer.Detach(self.mixers_tab)

        #Set up cues area
        self.cues.Build(mixer)
        self.cues_tab.Show()
        self.sizer.Insert(1, self.cues_tab, 9, wx.EXPAND)

        #Update all
        self.Layout()

    def OnDeEdit(self):
        """ OnDeEdit is called when the edit mode of a mixer is exited.

        Hides the cues editor and replaces it with the mixers area.
        Rebuilds the edited mixers view, as it has changed.
        """
        #Rebuilt CueView of the edited mixer
        self.editing.cue_view.Build()

        #Hide cues area
        self.cues_tab.Hide()
        self.sizer.Detach(self.cues_tab)

        #Show mixers area
        self.mixers_tab.Show()
        self.sizer.Insert(1, self.mixers_tab, 9, wx.EXPAND)

        #Reset editing mixer
        self.editing = None

        #Update all
        self.Layout()

    #-------------------------------------------
    #              Serialization
    #-------------------------------------------

    def serialize(self):
        return {"mixers" : self.mixers.serialize(),
                "sounds" : self.sounds.serialize(),
                "master" : self.master.serialize()}

    def deserialize(self, data):
        self.sounds.deserialize(data["sounds"])
        self.mixers.deserialize(data["mixers"])
        self.master.deserialize(data["master"])

#--------------------------------------------------------
#                        Master
#--------------------------------------------------------


class Master(wx.Panel):
    """ The left hand side panel,
    serving as the master controls for the project.
    """
    def __init__(self, project):
        wx.Panel.__init__(self, project)
        #Set default properties
        self.project = project
        self.volume = 1.0

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        #Add Volume slider
        self.slider = wx.Slider(self, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.slider.SetRange(0, 100)
        self.slider.SetValue(self.volume * 100)
        self.sizer.Add(self.slider, 1, wx.EXPAND)
        #Bind volume change event
        self.slider.Bind(wx.EVT_SLIDER, self._OnSlide)

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def _OnSlide(self, event):
        """ Event called when volume is changed.

        Set's the object's volume apropreately.
        """
        self.volume = self.slider.GetValue() / 100.0
        #Update the volume for all sounds
        for sound in self.project.sounds.sounds:
            sound.SetVolume(self.volume)

    #-------------------------------------------
    #              Serialization
    #-------------------------------------------

    def serialize(self):
        return {"volume" : self.volume}

    def deserialize(self, data):
        self.volume = float(data["volume"])
