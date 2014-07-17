""" This file includes all structures associated with the Mixer structure.
"""

import wx
import wx.lib.scrolledpanel as sc

from .structures import NameTextBox, clamp
from .cues import CuesView, Cue

#--------------------------------------------------------
#                       Classes
#--------------------------------------------------------

class Mixer(wx.Panel):
    def __init__(self, mixers, edit=True):
        wx.Panel.__init__(self, mixers, style=wx.RAISED_BORDER)
        self.mixers = mixers

        self.name = "Mixer"
        self.current_cue = 0
        self.cues = []

        #Make sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #Top bar
        top = wx.BoxSizer(wx.HORIZONTAL)

        self.name_box = NameTextBox(self, self.name, self.set_name, edit)
        top.Add(self.name_box, 1, wx.EXPAND)

        self.close_button = wx.Button(self, wx.ID_DELETE)
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose)
        top.Add(self.close_button, 0, wx.EXPAND)

        self.sizer.Add(top, 0, wx.EXPAND)
        self.sizer.AddSpacer(5)

        #Make cue View
        self.cue_view = CuesView(self)
        self.sizer.Add(self.cue_view, 1, wx.EXPAND)
        self.sizer.AddSpacer(5)

        #Buttons
        buttons = [
            ("Cue", self.OnCue),
            ("Back", self.OnBack),
            ("Reset", self.OnReset),
        ]

        for button_data in buttons:
            button = wx.Button(self, label=button_data[0])
            button.Bind(wx.EVT_BUTTON, button_data[1])
            self.sizer.Add(button, 0, wx.EXPAND)

        self.SetSizer(self.sizer)

    def _clamp_current_cue(self):
        self.current_cue = clamp(self.current_cue, 0, len(self.cues))

    def set_name(self, value):
        if value == self.name:
            return value
        def set(self=self, value=value):
            self.name = value
            self.name_box.SetValue(value)
        def reset(self=self, value=self.name):
            self.name = value
            self.name_box.SetValue(value)
        self.mixers.project.application.events.add(set, reset)
        return value

    def get_current_cue(self):
        if 0 <= self.current_cue < len(self.cues):
            return self.cues[self.current_cue]
        return None

    def add_cue(self):
        cue = Cue(self, "Cue " + str(len(self.cues) + 1))
        cue.index = len(self.cues)
        def do(self=self, cue=cue):
            self.cues.insert(cue.index, cue)
            self._clamp_current_cue()

            if self == self.mixers.project.editing:
                self.mixers.project.cues.OnCueAdd(cue)
            else:
                self.cue_view.Build()
        def undo(self=self, cue=cue):
            self.cues.pop(cue.index)
            self._clamp_current_cue()

            if self == self.mixers.project.editing:
                self.mixers.project.cues.OnCueRemove(cue)
            else:
                self.cue_view.Build()
        self.mixers.project.application.events.add(do, undo)

    def remove_cue(self, cue):
        def do(self=self, cue=cue):
            self.cues.pop(cue.index)
            self._clamp_current_cue()

            if self == self.mixers.project.editing:
                self.mixers.project.cues.OnCueRemove(cue)
            else:
                self.cue_view.Build()
        def undo(self=self, cue=cue):
            self.cues.insert(cue.index, cue)
            self._clamp_current_cue()

            if self == self.mixers.project.editing:
                self.mixers.project.cues.OnCueAdd(cue)
            else:
                self.cue_view.Build()
        self.mixers.project.application.events.add(do, undo)

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnSelect(self, cue=None):
        if not cue:
            cue = self.get_current_cue()
        else:
            self.current_cue = self.cues.index(cue)
        self.cue_view.OnSelect(cue)

    def OnClose(self, event):
        self.mixers.remove_mixer(self)

    def OnCue(self, event):
        if self.current_cue < len(self.cues):
            self.cues[self.current_cue].execute()
            self.current_cue += 1
        self.OnSelect()

    def OnBack(self, event):
        if self.current_cue > 0:
            self.current_cue -= 1
        self.OnSelect()

    def OnReset(self, event):
        self.current_cue = 0
        self.OnSelect()

    def OnEdit(self):
        self.sizer.Detach(self.cue_view)

    def OnDeEdit(self):
        self.sizer.Insert(1, self.cue_view)

    #-------------------------------------------
    #              Serialization
    #-------------------------------------------

    def serialize(self):
        return {"name" : self.name,
                "cues" : [c.serialize() for c in self.cues]}

    def deserialize(self, data):
        self.name = data["name"]
        self.cues = []
        for c in data["cues"]:
            cue = Cue(self, "")
            cue.deserialize(c)
            #Gather UI relevant data
            cue.index = len(self.cues)
            self.cues.append(cue)
        #Build UI
        self.cue_view.Build()


class Mixers(sc.ScrolledPanel):
    def __init__(self, project):
        sc.ScrolledPanel.__init__(self, project)
        self.project = project
        self.mixers = []

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.add_button = wx.Button(self, wx.ID_ADD)
        self.add_button.Bind(wx.EVT_BUTTON, self.OnAddMixer)
        self.sizer.Add(self.add_button, 0, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.SetupScrolling()

    def remove_mixer(self, mixer):
        undo, do = self._get_ar_mixer_events(mixer)
        self.project.application.events.add(do, undo)

    def _get_ar_mixer_events(self, mixer):
        def do(self=self, mixer=mixer):
            self.mixers.insert(mixer.index, mixer)
            self.sizer.Insert(mixer.index, mixer, 0, wx.EXPAND)
            mixer.Show()
            self.Layout()
            self.SetupScrolling()
        def undo(self=self, mixer=mixer):
            if self.project.editing == mixer:
                self.project.cues.OnBack(None)

            self.mixers.pop(mixer.index)
            self.sizer.Detach(mixer)
            mixer.Hide()
            self.Layout()
            self.SetupScrolling()
        return do, undo

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def OnAddMixer(self, event):
        mixer = Mixer(self)
        mixer.index = len(self.mixers)
        do, undo = self._get_ar_mixer_events(mixer)
        self.project.application.events.add(do, undo)

    #-------------------------------------------
    #              Serialization
    #-------------------------------------------

    def serialize(self):
        return [m.serialize() for m in self.mixers]

    def deserialize(self, data):
        for d in data:
            mixer = Mixer(self, edit=False)
            mixer.deserialize(d)
            #Setup GUI referneces
            mixer.index = len(self.mixers)
            self.mixers.append(mixer)
            self.sizer.Insert(mixer.index, mixer, 0, wx.EXPAND)
        #Reset GUI
        self.Layout()
        self.SetupScrolling()
