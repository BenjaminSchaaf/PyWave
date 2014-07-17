""" This file contains the EventManager class.

View the docs for EventManager for more information.
"""

class EventManager(object):
    """ EventManager is a generic undo-redo system.

    EventManager keeps track of events (sets of closures) in two queues (lists)
    for undo and redo functionality.
    Events are kept track of indefinitely, but memory shouldn't be an issue.
    """
    def __init__(self):
        self.undo_queue = []
        self.redo_queue = []

    def reset(self):
        """ Reset all events.

        CLears both the undo and redo queues.
        This action is not undoable.
        """
        del self.undo_queue[:]
        del self.redo_queue[:]

    def add(self, do_event, undo_event):
        """ Add an event to the undo queue, executing that event.

        do and undo are both closures.
        undo should reverse any changes that do may do,
        but EventManager does not regulate it.
        In general, if one calls do and then undo, the target state should
        be identical to what it was before.
        """
        #Execute the event
        do_event()
        #Update the undo queue
        self.undo_queue.insert(0, (do_event, undo_event))
        #Clear the redo queue
        del self.redo_queue[:]

    def undo(self):
        """ Calls the undo function of the last event.
        """
        if len(self.undo_queue) > 0:
            #Call undo of the first event in the undo queue
            event = self.undo_queue.pop(0)
            event[1]()
            #Add that event into the redo queue
            self.redo_queue.insert(0, event)

    def redo(self):
        """ Calls the do function of the last undone event.
        """
        if len(self.redo_queue) > 0:
            #Call do of the first event in the redo queue
            event = self.redo_queue.pop(0)
            event[0]()
            #Add that event back into the undo queue
            self.undo_queue.insert(0, event)
