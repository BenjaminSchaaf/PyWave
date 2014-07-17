""" This file contains all structures associated with the Sound structure.
"""

import os

import wx
import pygame
import wx.lib.scrolledpanel as sc

from .structures import NameTextBox

#--------------------------------------------------------
#                       Classes
#--------------------------------------------------------

class Sound(wx.Panel):
    """ The structure of a single Sound.

    Contains links to the sound file, as well as the actual
    sound loaded with pygame.
    """
    def __init__(self, sounds, path=None, edit=True):
        wx.Panel.__init__(self, sounds, style=wx.RAISED_BORDER)
        self.sounds = sounds
        self.index = -1

        #Load the sound if possible
        if path:
            self.name = os.path.basename(path)
            self.path = path
            self.sound = pygame.mixer.Sound(path)
        else:
            self.name = ""
            self.path = ""
            self.sound = None

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        self.name_box = NameTextBox(self, self.name, self.OnSetName, edit)
        self.sizer.Add(self.name_box, 1, wx.EXPAND)

        self.delete_button = wx.Button(self, wx.ID_DELETE)
        self.delete_button.Bind(wx.EVT_BUTTON, self.OnDelete)
        self.sizer.Add(self.delete_button, 0, wx.EXPAND)

    def __nonzero__(self):
        return bool(self.sound)

    def set_volume(self, volume):
        """ Set the volume of the associated sound.
        """
        self.sound.set_volume(volume)

    def get_length(self):
        """ Return the length in second of the associated sound.
        """
        return self.sound.get_length()*1000

    def play(self, fade):
        """ Play the sound, with set fade in in ms.
        """
        fade = int(fade)
        self.sound.play(fade_ms=fade)

    def stop(self, fade):
        """ Stop playing the sound, with set fade out in ms.
        """
        fade = int(fade)
        self.sound.fadeout(fade)

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnDelete(self, event=None):
        """ Event called when the sound is deleted.
        """
        self.sounds.remove_sound(self)

    def OnSetName(self, value):
        """ Event called when the name of the sound has been changed.

        Adds the name change to the EventManager and returns the accepted name.
        """
        #Ignore, if the name hasn't changed
        if value == self.name:
            return value
        #Create do and undo closures
        def do(self=self, value=value):
            self.name = value
            self.name_box.SetValue(value)

            #Notify the cue editor
            if self.sounds.project.editing:
                self.sounds.project.cues.OnSoundsChange()
        def undo(self=self, value=self.name):
            self.name = value
            self.name_box.SetValue(value)

            #Notify the cue editor
            if self.sounds.project.editing:
                self.sounds.project.cues.OnSoundsChange()
        #Add the event
        self.sounds.project.application.events.add(do, undo)
        return value

    #-------------------------------------------
    #              Serialization
    #-------------------------------------------

    def serialize(self):
        return {"path" : self.path,
                "name" : self.name}

    def deserialize(self, data):
        self.path = str(data["path"])
        self.sound = pygame.mixer.Sound(self.path)
        self.name = str(data["name"])

class Sounds(sc.ScrolledPanel):
    """ The UI for the collection of sounds.
    """
    def __init__(self, project):
        sc.ScrolledPanel.__init__(self, project)
        self.project = project

        self.sounds = []

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.add_button = wx.Button(self, wx.ID_ADD)
        self.add_button.Bind(wx.EVT_BUTTON, self.OnAddSound)
        self.sizer.Add(self.add_button, 0, wx.EXPAND)

        #Setup panel
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.SetupScrolling()

    def add_sound(self, sound):
        """ Adds a sound object to the list of sounds.
        """
        sound.index = len(self.sounds)
        do_event, undo_event = self._get_ar_sound_events(sound)
        self.project.application.events.add(do_event, undo_event)

    def remove_sound(self, sound):
        """ Removes a sound object from the list of sounds.
        """
        undo_event, do_event = self._get_ar_sound_events(sound)
        self.project.application.events.add(do_event, undo_event)

    def _get_ar_sound_events(self, sound):
        """ Return a do and undo event for a deletion or addition of a sound
        object.
        """
        #Find affected mixers
        affected = []
        for mixer in self.project.mixers.mixers:
            for cue in mixer.cues:
                if cue.sound == sound:
                    affected.append(cue)
        #Define the add and remove functions for that sound
        def add(self=self, sound=sound, affected=affected):
            self.sounds.insert(sound.index, sound)
            self.sizer.Insert(sound.index, sound, 0, wx.EXPAND)
            sound.Show()

            #Update affected cues
            for cue in affected:
                cue.sound = sound

            #Inform cue editor of new sound
            if self.project.editing:
                self.project.cues.OnSoundsChange()

            #Perform layout operations
            self.Layout()
            self.SetupScrolling()
        def remove(self=self, sound=sound, affected=affected):
            self.sounds.pop(sound.index)
            self.sizer.Detach(sound)
            sound.Hide()

            #update affected cues
            for cue in affected:
                cue.sound = None

            #Inform cue editor of deleted sound
            if self.project.editing:
                self.project.cues.OnSoundsChange()

            #Perform layout operations
            self.Layout()
            self.SetupScrolling()
        return add, remove

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnAddSound(self, event=None):
        """ Even called when a sound is added.

        Opens a dialog for wav files.
        """
        dialog = wx.FileDialog(self, "Open Sound File", "", "",
                               "Sound File (*.wav)|*.wav",
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        #Exit events
        status = dialog.ShowModal()
        if status == wx.ID_CANCEL:
            return

        #Load the found file
        path = dialog.GetPath()
        sound = Sound(self, path)
        self.add_sound(sound)

    #-------------------------------------------
    #              Serialization
    #-------------------------------------------

    def serialize(self):
        return [s.serialize() for s in self.sounds]

    def deserialize(self, data):
        for sdata in data:
            sound = Sound(self, edit=False)
            sound.deserialize(sdata)
            #Setup GUI referneces
            sound.index = len(self.sounds)
            self.sounds.append(sound)
            self.sizer.Insert(len(self.sounds) - 1, sound, 0, wx.EXPAND)
        #Reset GUI
        self.Layout()
        self.SetupScrolling()
