""" This file holds all classes related to the Cue structure
"""

import wx
import wx.lib.scrolledpanel as sc

from .structures import NameTextBox, IndexComboBox, TimeValue

#--------------------------------------------------------
#                         Cue
#--------------------------------------------------------

class Cue(object):
    """ The structure for a single Cue object.

    This structure does not contain any UI.
    """
    PLAY = 1
    STOP = 2
    names = ["Play", "Stop"]

    def __init__(self, mixer, name):
        self.mixer = mixer
        self.name = name
        self.type = 0
        self.sound = None
        self.fade = TimeValue()

    def execute(self):
        """ Execute the cue according to it's type and associated sound.
        """
        if not self.sound:
            return

        #Play or Stop sound
        length = self.sound.GetLength()
        if self.type == Cue.PLAY:
            self.sound.Play(self.fade.eval(length))
        elif self.type == Cue.STOP:
            self.sound.Stop(self.fade.eval(length))

    #-------------------------------------------
    #              Serialization
    #-------------------------------------------

    def serialize(self):
        sound_index = self.sound.index if self.sound else -1
        return {"type" : self.type,
                "name" : self.name,
                "sound" : sound_index,
                "fade" : str(self.fade)}

    def deserialize(self, data):
        self.type = int(data["type"])
        self.name = str(data["name"])
        sound_index = int(data["sound"])
        if sound_index < 0:
            self.sound = None
        else:
            self.sound = self.mixer.mixers.project.sounds.sounds[sound_index]
        self.fade = TimeValue(data["fade"])

#--------------------------------------------------------
#                       CueViews
#--------------------------------------------------------

class CuesView(wx.Panel):
    def __init__(self, mixer):
        wx.Panel.__init__(self, mixer, style=wx.SUNKEN_BORDER)
        self.mixer = mixer

        #Make Sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #Top
        top = wx.BoxSizer(wx.HORIZONTAL)

        #Title
        title = wx.StaticText(self, label="Cues")
        top.Add(title, 1, wx.EXPAND)

        #Edit button
        self.edit = wx.Button(self, wx.ID_EDIT)
        self.edit.Bind(wx.EVT_BUTTON, self._OnEdit)
        top.Add(self.edit, 0, wx.EXPAND)

        self.sizer.Add(top, 0, wx.EXPAND)

        #Make scrolled cue view
        self.cue_view = sc.ScrolledPanel(self)
        self.cue_views = []

        #Make cue view sizer
        self.cv_sizer = wx.BoxSizer(wx.VERTICAL)

        #Setup cue view
        self.cue_view.SetSizer(self.cv_sizer)
        self.cue_view.SetAutoLayout(True)
        self.cue_view.SetupScrolling()

        #Size cue view
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.cue_view, 1, wx.EXPAND)

        self.SetSizer(self.sizer)

    def Build(self):
        """ Build all contained CueView structures.

        Also destroys any previously present CueViews.
        """
        for cue_view in self.cue_views:
            cue_view.Destroy()
        self.cue_views = []

        found = False
        for cue in self.mixer.cues:
            cue_view = CueView(self.cue_view, self, cue)
            if cue == self.mixer.get_current_cue():
                cue_view.SetBackgroundColour((125, 255, 125))
                found = True
            elif not found:
                cue_view.SetBackgroundColour((255, 125, 125))
            #Force update
            cue_view.Refresh()
            cue_view.Update()
            self.cv_sizer.Add(cue_view, 0, wx.EXPAND)
            self.cue_views.append(cue_view)

        self.Layout()
        self.cue_view.SetupScrolling()

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnSelect(self, cue):
        """ Event called when a cue from the cue views is selected.
        """
        found = False
        for i in xrange(len(self.cue_views)):
            cue_view = self.cue_views[i]

            #Find the selected cue
            if cue_view.cue == cue:
                #Mark the current cue with light green
                cue_view.SetBackgroundColour((125, 255, 125))

                #Get previous CueView, 4 spaces up
                previous_index = min(i + 4, len(self.cue_views) - 1)
                previous_cue_view = self.cue_views[previous_index]
                #Get next CueView, 4 spaces down
                next_index = max(i - 4, 0)
                next_cue_view = self.cue_views[next_index]

                #Ensure we always see the past and next 4 cues
                self.cue_view.ScrollChildIntoView(previous_cue_view)
                self.cue_view.ScrollChildIntoView(next_cue_view)

                #Ensure we definitely see the current cue
                self.cue_view.ScrollChildIntoView(cue_view)

                found = True
            elif found:
                #Mark all upcomming cues with normal colours
                cue_view.SetBackgroundColour(wx.NullColour)
            else:
                #Mark all executed cues with light red
                cue_view.SetBackgroundColour((255, 125, 125))

    def _OnEdit(self, event):
        self.mixer.mixers.project.OnEdit(self.mixer)

class CueView(wx.Panel):
    def __init__(self, parent, cues, cue):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER)
        self.cues = cues
        self.cue = cue

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.label = wx.StaticText(self, label=cue.name)
        self.sizer.Add(self.label, 1, wx.EXPAND)

        self.SetSizer(self.sizer)

        #Bind mouse events
        self.label.Bind(wx.EVT_LEFT_DOWN, self.OnSelect)
        self.label.Bind(wx.EVT_LEAVE_WINDOW, self.OnExit)
        self.label.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnSelect(self, event):
        self.cues.mixer.OnSelect(self.cue)

    def OnExit(self, event):
        colour = list(self.GetBackgroundColour())
        colour[2] -= 20
        self.label.SetBackgroundColour(colour)

    def OnEnter(self, event):
        colour = list(self.GetBackgroundColour())
        colour[2] += 20
        self.label.SetBackgroundColour(colour)

#--------------------------------------------------------
#                     CueEditors
#--------------------------------------------------------

class CuesEditor(sc.ScrolledPanel):
    def __init__(self, project):
        sc.ScrolledPanel.__init__(self, project)
        self.project = project
        self.mixer = None
        self.cues = []

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.top = wx.BoxSizer(wx.HORIZONTAL)

        self.title = wx.StaticText(self)
        self.top.Add(self.title)

        self.top.AddStretchSpacer()

        self.back = wx.Button(self, wx.ID_BACKWARD)
        self.back.Bind(wx.EVT_BUTTON, self.OnBack)
        self.top.Add(self.back)

        self.sizer.Add(self.top, 0, wx.EXPAND)
        self.sizer.AddSpacer(5)

        self.add = wx.Button(self, wx.ID_ADD)
        self.add.Bind(wx.EVT_BUTTON, self.OnAdd)
        self.sizer.AddSpacer(5)
        self.sizer.Add(self.add, 0, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.SetupScrolling()

    def add_editor(self, cue):
        editor = CueEditor(self, cue)
        self.sizer.Insert(cue.index + 2, editor, 0,  wx.EXPAND)
        self.cues.append(editor)

    def remove_editor(self, cue):
        for editor in self.cues:
            if editor.cue == cue:
                self.ScrollChildIntoView(editor)
                self.cues.remove(editor)
                editor.Destroy()
                return

    def Build(self, mixer):
        self.title.SetLabel(mixer.name)
        self.mixer = mixer

        for cue in mixer.cues:
            self.add_editor(cue)

        self.Layout()
        self.SetupScrolling()

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnBack(self, event):
        self.mixer = None
        for cue in self.cues:
            cue.Destroy()
        self.cues = []
        self.project.OnDeEdit()

    def OnAdd(self, event):
        self.mixer.add_cue()

    def OnDelete(self, editor):
        self.mixer.remove_cue(editor.cue)

    def OnCueAdd(self, cue):
        self.add_editor(cue)

        self.Layout()
        self.SetupScrolling()
        self.ScrollChildIntoView(self.add)

    def OnCueRemove(self, cue):
        self.remove_editor(cue)

        self.Layout()
        self.SetupScrolling()

    def OnSoundsChange(self):
        for cue in self.cues:
            cue.OnSoundsChange()

class CueEditor(wx.Panel):
    def __init__(self, cues, cue):
        wx.Panel.__init__(self, cues, style=wx.SUNKEN_BORDER)
        self.cues = cues
        self.cue = cue

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Name Box
        self.name_box = NameTextBox(self, cue.name, self.set_name)
        self.sizer.Add(self.name_box, 1, wx.EXPAND)

        #Type selection
        type_names = ["Select a action..."] + Cue.names
        self.type_selection = IndexComboBox(self, cue.type, type_names, self.OnTypeSelect)
        self.sizer.Add(self.type_selection, 1, wx.EXPAND)

        #Sound selection
        sound_names = self.get_sound_names()
        if cue.sound:
            index = cue.sound.index + 1
        else:
            index = 0
        self.sound_selection = IndexComboBox(self, index, sound_names, self.OnSoundSelect)
        self.sizer.Add(self.sound_selection, 1, wx.EXPAND)

        self.delete_button = wx.Button(self, wx.ID_DELETE)
        self.delete_button.Bind(wx.EVT_BUTTON, self.OnDelete)
        self.sizer.Add(self.delete_button, 0, wx.EXPAND)

        self.SetSizer(self.sizer)

    def get_sound_names(self):
        return ["Select a sound..."] + [s.name for s in self.cues.mixer.mixers.project.sounds.sounds]

    def set_name(self, value):
        if value == self.cue.name:
            return value
        def set(cues=self.cues, cue=self.cue, value=value):
            cue.name = value
            if cues.mixer == cue.mixer:
                cues.cues[cue.index].name_box.SetValue(value)
            else:
                cue.mixer.cue_view.Build()
        def reset(cues=self.cues, cue=self.cue, value=self.cue.name):
            cue.name = value
            if cues.mixer == cue.mixer:
                cues.cues[cue.index].name_box.SetValue(value)
            else:
                cue.mixer.cue_view.Build()
        self.cues.mixer.mixers.project.application.events.add(set, reset)
        return value

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnDelete(self, event):
        self.cues.OnDelete(self)

    def OnTypeSelect(self, type):
        if type == self.cue.type:
            return type
        def set(cues=self.cues, cue=self.cue, type=type):
            cue.type = type
            if cues.mixer == cue.mixer:
                cues.cues[cue.index].type_selection.SetValue(type)
            else:
                cue.mixer.cue_view.Build()
        def reset(cues=self.cues, cue=self.cue, type=self.cue.type):
            cue.type = type
            if cues.mixer == cue.mixer:
                cues.cues[cue.index].type_selection.SetValue(type)
            else:
                cue.mixer.cue_view.Build()
        self.cues.mixer.mixers.project.application.events.add(set, reset)
        return type

    def OnSoundSelect(self, index):
        if not self.cue.sound and index == 0:
            return
        elif self.cue.sound and self.cue.sound.index == index - 1:
            return
        def set(cues=self.cues, cue=self.cue, index=index):
            if index == 0:
                cue.sound = None
            else:
                cue.sound = cues.project.sounds.sounds[index - 1]

            if cues.mixer == cue.mixer:
                cues.cues[cue.index].sound_selection.SetValue(index)
            else:
                cue.mixer.cue_view.Build()
        def reset(cues=self.cues, cue=self.cue, sound=self.cue.sound):
            cue.sound = sound
            if cues.mixer == cue.mixer:
                if sound:
                    index = sound.index + 1
                else:
                    index = 0
                cues.cues[cue.index].sound_selection.SetValue(index)
            else:
                cue.mixer.cue_view.Build()
        self.cues.mixer.mixers.project.application.events.add(set, reset)
        return index

    def OnSoundsChange(self):
        self.sound_selection.SetValues(self.get_sound_names())
        if self.cue.sound:
            self.sound_selection.SetValue(self.cue.sound.index + 1)
        else:
            self.sound_selection.SetValue(0)
