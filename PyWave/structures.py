""" This file contains definitions for tools and extensions to make
building the rest of the application easier.

Extensions come in the form of GUI elements.
Tools come in the form of extra mathematical functions,
or special value handling classes.
"""

import wx
import wx.lib.scrolledpanel as sc

#--------------------------------------------------------
#                 GUI Extension Classes
#--------------------------------------------------------

class IndexComboBox(wx.ComboBox):
    """ A wx.ComboBox with a callback that works via a index based interface,
    rather than the standard name.
    """

    def __init__(self, parent, value, values, callback):
        #Make default combo-box setup
        wx.ComboBox.__init__(self, parent, wx.CB_DROPDOWN | wx.CB_SORT,
                             value=values[value], choices=values,
                             style=wx.CB_READONLY)
        #Bind the local callback
        self.Bind(wx.EVT_COMBOBOX, self._OnComboboxChange)

        #reference the values
        self.callback = callback
        self.values = values

    def SetValue(self, value):
        """ Set the value by the index of it's values.

        Wraps the SetValue of the ComboBox in an index based interface.
        """
        wx.ComboBox.SetValue(self, self.values[value])

    def SetValues(self, values):
        """ Set the values of the combo box.

        Values are also kept track of by the python object.
        """
        #Clear the ComboBox
        self.Clear()
        #Set values in ComboBox
        for value in values:
            self.Append(value)
        #Keep a copy
        self.values = list(values)

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def _OnComboboxChange(self, event):
        """ Callback for combobox changes.
        Calls the set callback function.
        """
        #Get the index of the element selected
        index = self.values.index(self.GetValue())
        #Call the callback with the index
        self.callback(index)

class Tab(wx.StaticBoxSizer):
    """ A StaticBoxSizer, with a nicer interface.

    Used for the individual areas/tabs.
    """
    def __init__(self, parent, child, title):
        self.child = child
        #Make a static box to wrap the child in
        self.tab = wx.StaticBox(parent, label=title)

        #Make the sizer for the static box
        wx.StaticBoxSizer.__init__(self, self.tab, wx.VERTICAL)

        #Add the child to the sizer
        self.Add(child, True, wx.EXPAND)

    def Hide(self):
        """ Hides the tab and it's child.
        """
        self.tab.Hide()
        self.child.Hide()

    def Show(self):
        """ Shows the tab and it's child.
        """
        self.tab.Show()
        self.child.Show()

class NameTextBox(sc.ScrolledPanel):
    """ A self-contained, editable label.

    Makes simple labels editable through the use of double clicks.
    NameTextBox have vigerous size restrictions due to wxPython wierdnesses.
    """

    def __init__(self, parent, value, callback, open=False):
        #Setup Panel
        sc.ScrolledPanel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.callback = callback
        self.mode = 0

        #Restrict the size
        self.SetMinSize((200, 30))

        #Make sizer
        self.sizer = sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        #Convert default value to string
        value = str(value)

        #Make TextControl widget
        self.input = wx.TextCtrl(self, value=value, style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.input, True, wx.EXPAND | wx.ALIGN_CENTRE)
        #Show it
        self.input.Show()

        #Make the label widget
        self.label = wx.StaticText(self, label=value)
        sizer.Add(self.label, True, wx.EXPAND | wx.ALIGN_CENTRE)
        #Hide it
        self.label.Hide()

        #Refresh the layout
        self.Layout()
        self.SetAutoLayout(True)
        self.SetupScrolling()

        #Start editing the label if open
        if open:
            self.StartInput()
        else:
            self.CancelInput()

        #Bind events
        self.label.Bind(wx.EVT_LEFT_DCLICK, self._OnEnter)
        self.input.Bind(wx.EVT_KEY_DOWN, self._OnKeyEvent)
        self.input.Bind(wx.EVT_KILL_FOCUS, self._OnExit)
        self.input.Bind(wx.EVT_TEXT_ENTER, self._OnExit)

    def SetValue(self, value):
        """ Set the value of the named label.
        """
        #Update both the label and input box
        self.label.SetLabel(value)
        self.input.SetLabel(value)

    def StartInput(self):
        """ Starts the label editing.

        Switches from a label to a text box.
        """
        #Set the text control value
        self.input.SetValue(str(self.label.GetLabel()))

        #Show the text control
        self.input.Show()
        #Hide the label
        self.label.Hide()
        #Perform a layout operation
        self.Layout()
        self.SetupScrolling()

        #Set the selection and mode
        self.input.SetSelection(0, -1)
        self.input.SetFocus()
        self.mode = 0

    def EndInput(self):
        """ Stops the label editing.

        Switches from a text box to a label, and calls the callback.
        """
        #Set the label value
        self.label.SetLabel(str(self.callback(self.input.GetValue())))
        #cancel the input
        self.CancelInput()

    def CancelInput(self):
        """ Stops the label editing.

        Reverts back to what it was before.
        """
        #Show the label
        self.label.Show()
        #Hide the text control
        self.input.Hide()
        #Performa a layout operation
        self.Layout()
        self.SetupScrolling()

        #Set the mode
        self.mode = 1

    #-------------------------------------------
    #                  Events
    #-------------------------------------------

    def _OnEnter(self, event):
        """ Event called when input box is entered.

        Starts the input.
        """
        self.StartInput()

    def _OnExit(self, event):
        """ Event called when input box is exited.

        Stops the input.
        """
        self.EndInput()

    def _OnKeyEvent(self, event):
        """ Event for key inputs.

        Handels escapes and returns correctly.
        """
        #Get Keycode
        code = event.RawKeyCode
        #Perform actions according to keycode
        if code in [wx.WXK_CANCEL, wx.WXK_ESCAPE]:
            self.CancelInput()
        elif code in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
            self.EndInput()
        else:
            #continue with input
            event.Skip()

#--------------------------------------------------------
#                   Non-UI Classes
#--------------------------------------------------------

class TimeValue(object):
    """ A TimeValue is a floating point number associated with a specific
    time unit, such as seconds or milliseconds.

    TimeValues are given by string inputs of the floating point number,
    followed by the unit's initials.

    Other supported units include relative units such as %.
    """

    #-------------------------------------------
    #                  Constants
    #-------------------------------------------

    #All possible characters used for numbers
    NUMBER_CHARS = set("0123456789.-+")
    #Unit mappings to the internal value
    units = {
        "ms" : lambda value, length: value,
        "s" : lambda value, length: value * 1000,
        "m" : lambda value, length: value * 1000 * 60,
        "%" : lambda value, length: length * (value / 100),
    }

    #-------------------------------------------
    #              Class Methods
    #-------------------------------------------

    def __new__(cls, value="0s"):
        """ Return a new instance of TimeValue for a given value.
        If the value was not parsable or otherwise determinable, return None.
        """
        #Copy other TimeValues
        if isinstance(value, TimeValue):
            value = value.number, value.unit
        #parse the value otherwise
        else:
            value = cls._parse(value)

        #Return TimeValue instance if value is defined
        if value is not None:
            return super(TimeValue, cls).__new__(cls, value[0], value[1])
        #Return None otherwise
        else:
            return None

    @classmethod
    def _parse(cls, value):
        """ Parse value as a string.
        Returns a tuple containing the parsed number and unit.
        Returns None if parsing failed.
        """
        #Find the location where the value stops being a number
        split_location = 0
        while value[split_location] in cls.NUMBER_CHARS:
            split_location += 1
        split_location += 1

        #Try to convert the number part of the value into a float
        try:
            number = float(value[:split_location])
        #On fail, return none
        except Exception:
            return None

        #Find whether the non-number part of the value is a unit
        unit = value[split_location:]
        if unit not in cls.units:
            return None

        #If everything is good, return a tuple of number and unit
        return number, unit

    #-------------------------------------------
    #             Instance Methods
    #-------------------------------------------

    def __init__(self, number, unit):
        self.number = number
        self.unit = unit

    def __str__(self):
        """ Return the TimeValue converted back to a string.
        The format is identical to the input format.
        """
        return ''.join((self.number, self.unit))

    def eval(self, length):
        """ Evaluate the real value (in ms) of the TimeValue,
        given a relative length also in ms.
        """
        #Get the unit conversion function from the class
        conversion_function = self.__class__.units[self.unit]
        #Convert the units
        return conversion_function(self.number, length)

#--------------------------------------------------------
#                   GUI Functions
#--------------------------------------------------------

def ShowError(parent, title, message):
    """ Shows a standard error message.

    Error message is titled with a message, is centered and has an OK button.
    Does not return anything.
    """
    dialog = wx.MessageDialog(parent, message, title,
                              wx.OK | wx.ICON_ERROR | wx.CENTRE)
    dialog.ShowModal()
    dialog.Destroy()

#--------------------------------------------------------
#                  Non-UI Functions
#--------------------------------------------------------

def clamp(value, _min, _max):
    """ Return a value clamped between a _min value and a _max value.
    """
    return max(min(value, _max), _min)
