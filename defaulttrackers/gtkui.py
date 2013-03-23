#
# gtkui.py
#
# Copyright (C) 2013 Stefan Talpalaru <stefantalpalaru@yahoo.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
# Copyright (C) 2010 Pedro Algarvio <pedro@algarvio.me>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

import gtk
import logging

from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common
from deluge.ui.gtkui import dialogs
from pprint import pprint

from common import get_resource

log = logging.getLogger(__name__)

def iter_prev(iter, model):
    path = model.get_path(iter)
    position = path[-1]
    if position == 0:
        return None
    prev_path = list(path)[:-1]
    prev_path.append(position - 1)
    prev = model.get_iter(tuple(prev_path))
    return prev

class OptionsDialog():
    def __init__(self, gtkui):
        self.gtkui = gtkui

    def show(self, options=None, item_id=None, item_index=None):
        self.glade = gtk.glade.XML(get_resource("options.glade"))
        self.glade.signal_autoconnect({
            "on_opts_add_button_clicked": self.on_add,
            "on_opts_apply_button_clicked": self.on_apply,
            "on_opts_cancel_button_clicked": self.on_cancel,
            "on_options_dialog_close": self.on_cancel,
        })
        self.dialog = self.glade.get_widget("options_dialog")
        self.dialog.set_transient_for(component.get("Preferences").pref_dialog)

        if item_id:
            #We have an existing item_id, we are editing
            self.glade.get_widget("opts_add_button").hide()
            self.glade.get_widget("opts_apply_button").show()
            self.item_id = item_id
        else:
            #We don't have an id, adding
            self.glade.get_widget("opts_add_button").show()
            self.glade.get_widget("opts_apply_button").hide()
            self.item_id = None
        self.item_index = item_index

        self.load_options(options)
        self.dialog.run()
        self.dialog.destroy()

    def load_options(self, options):
        if options:
            self.glade.get_widget("tracker_entry").set_text(options.get("url", ""))

    def on_add(self, widget):
        try:
            options = self.generate_opts()
            self.gtkui.store.append([options["url"]])
            self.gtkui.trackers.append({"url": options["url"]})
        except Exception, err:
            dialogs.ErrorDialog("Error", str(err), self.dialog).run()

    def generate_opts(self):
        # generate options dict based on gtk objects
        options = {
            "url": self.glade.get_widget("tracker_entry").get_text(),
        }
        if len(options["url"]) == 0:
            raise Exception("empty URL")
        return options

    def on_apply(self, widget):
        try:
            options = self.generate_opts()
            self.gtkui.store[self.item_id][0] = options["url"]
            self.gtkui.trackers[self.item_index]["url"] = options["url"]
        except Exception, err:
            dialogs.ErrorDialog("Error", str(err), self.dialog).run()

    def on_cancel(self, widget):
        self.dialog.response(gtk.RESPONSE_DELETE_EVENT)

class GtkUI(GtkPluginBase):
    def enable(self):
        self.glade = gtk.glade.XML(get_resource("config.glade"))
        self.glade.signal_autoconnect({
            "on_add_button_clicked": self.on_add_button_clicked,
            "on_edit_button_clicked": self.on_edit_button_clicked,
            "on_remove_button_clicked": self.on_remove_button_clicked,
            "on_up_button_clicked": self.on_up_button_clicked,
            "on_down_button_clicked": self.on_down_button_clicked,
        })

        component.get("Preferences").add_page("Default Trackers", self.glade.get_widget("prefs_box"))
        component.get("PluginManager").register_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").register_hook("on_show_prefs", self.on_show_prefs)

        self.trackers = []
        scrolled_window = self.glade.get_widget("scrolledwindow1")
        self.store = self.create_model()
        self.tree_view = gtk.TreeView(self.store)
        self.tree_view.connect("cursor-changed", self.on_listitem_activated)
        self.tree_view.connect("row-activated", self.on_edit_button_clicked)
        self.tree_view.set_rules_hint(True)
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("URL", rendererText, text=0)
        self.tree_view.append_column(column)
        scrolled_window.add(self.tree_view)
        scrolled_window.show_all()

        self.opts_dialog = OptionsDialog(self)

    def disable(self):
        component.get("Preferences").remove_page("DefaultTrackers")
        component.get("PluginManager").deregister_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").deregister_hook("on_show_prefs", self.on_show_prefs)

    def on_apply_prefs(self):
        log.debug("applying prefs for DefaultTrackers")
        config = {
            "trackers": [{"url": str(row[0])} for row in self.store]
        }
        client.defaulttrackers.set_config(config)

    def on_show_prefs(self):
        client.defaulttrackers.get_config().addCallback(self.cb_get_config)

    def cb_get_config(self, config):
        "callback for on show_prefs"
        self.trackers = config["trackers"]
        self.store.clear()
        for tracker in self.trackers:
            self.store.append([tracker["url"]])
        # Workaround for cached glade signal appearing when re-enabling plugin in same session
        if self.glade.get_widget("edit_button"):
            # Disable the remove and edit buttons, because nothing in the store is selected
            self.glade.get_widget("remove_button").set_sensitive(False)
            self.glade.get_widget("edit_button").set_sensitive(False)
            self.glade.get_widget("up_button").set_sensitive(False)
            self.glade.get_widget("down_button").set_sensitive(False)

    def create_model(self):
        store = gtk.ListStore(str)
        for tracker in self.trackers:
            store.append([tracker["url"]])
        return store

    def on_listitem_activated(self, treeview):
        tree, tree_id = self.tree_view.get_selection().get_selected()
        if tree_id:
            self.glade.get_widget("edit_button").set_sensitive(True)
            self.glade.get_widget("remove_button").set_sensitive(True)
            self.glade.get_widget("up_button").set_sensitive(True)
            self.glade.get_widget("down_button").set_sensitive(True)
        else:
            self.glade.get_widget("edit_button").set_sensitive(False)
            self.glade.get_widget("remove_button").set_sensitive(False)
            self.glade.get_widget("up_button").set_sensitive(False)
            self.glade.get_widget("down_button").set_sensitive(False)

    def on_add_button_clicked(self, widget):
        self.opts_dialog.show()

    def on_remove_button_clicked(self, widget):
        tree, tree_id = self.tree_view.get_selection().get_selected()
        index = self.tree_view.get_selection().get_selected_rows()[1][0][0]
        self.store.remove(tree_id)
        del self.trackers[index]

    def on_edit_button_clicked(self, widget):
        tree, tree_id = self.tree_view.get_selection().get_selected()
        index = self.tree_view.get_selection().get_selected_rows()[1][0][0]
        url = str(self.store.get_value(tree_id, 0))
        if url:
            self.opts_dialog.show({
                "url": url,
            }, tree_id, index)

    def on_up_button_clicked(self, widget):
        tree, tree_id = self.tree_view.get_selection().get_selected()
        if tree_id is not None:
            prev = iter_prev(tree_id, self.store)
            if prev is not None:
                self.store.swap(prev, tree_id)

    def on_down_button_clicked(self, widget):
        tree, tree_id = self.tree_view.get_selection().get_selected()
        if tree_id is not None:
            nexti = self.store.iter_next(tree_id)
            if nexti is not None:
                self.store.swap(tree_id, nexti)

