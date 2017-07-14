import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

# Constants
BOX_SPACING = 5
PADDING = 5
WORKSHOP_CONFIG_DIRECTORY = "workshop_configs"
VBOXMANAGE_DIRECTORY = "C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"


# This class is a general message dialog with entry
class EntryDialog(Gtk.Dialog):

    def __init__(self, parent, message):
        Gtk.Dialog.__init__(self, "Name", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        # This is the outer box, we need another box inside for formatting
        self.dialogBox = self.get_content_area()
        self.outerVertBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)

        self.dialogBox.add(self.outerVertBox)

        self.label = Gtk.Label(message)
        self.entry = Gtk.Entry()
        self.entryText = None

        self.outerVertBox.pack_start(self.label, False, False, PADDING)
        self.outerVertBox.pack_start(self.entry, False, False, PADDING)
        self.set_modal(True)

        self.connect("response", self.dialogResponseActionEvent)

        self.show_all()

        self.status = None

    def dialogResponseActionEvent(self, dialog, responseID):
        # OK was clicked and there is text
        if responseID == Gtk.ResponseType.OK and not self.entry.get_text_length() < 1:
            self.entryText = self.entry.get_text()
            self.status = True

        # Ok was clicked and there is no text
        elif responseID == Gtk.ResponseType.OK and self.entry.get_text_length() < 1:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, "The entry must not be empty.")
            dialog.run()
            dialog.destroy()

        # The operation was canceled
        elif responseID == Gtk.ResponseType.CANCEL or responseID == Gtk.ResponseType.DELETE_EVENT:
            self.entryText = None
            self.status = True
