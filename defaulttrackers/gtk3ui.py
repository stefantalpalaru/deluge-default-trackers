# -*- coding: utf-8 -*-
# gtkui.py
#
# Copyright (C) 2013-2022 Ștefan Talpalaru <stefantalpalaru@yahoo.com>
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

from __future__ import absolute_import, unicode_literals
from gi.repository import Gtk
import logging
import os

from deluge.ui.client import client
from deluge.plugins.pluginbase import Gtk3PluginBase
import deluge.component as component
from deluge.ui.gtk3 import dialogs
#from pprint import pprint

from .common import get_resource

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
        self.builder = Gtk.Builder.new_from_file(get_resource("options.ui"))
        self.builder.connect_signals({
            "on_opts_add_button_clicked": self.on_add,
            "on_opts_apply_button_clicked": self.on_apply,
            "on_opts_cancel_button_clicked": self.on_cancel,
            "on_options_dialog_close": self.on_cancel,
        })
        self.dialog = self.builder.get_object("options_dialog")
        self.dialog.set_transient_for(component.get("Preferences").pref_dialog)

        if item_id:
            #We have an existing item_id, we are editing
            self.builder.get_object("opts_add_button").hide()
            self.builder.get_object("opts_apply_button").show()
            self.item_id = item_id
        else:
            #We don't have an id, adding
            self.builder.get_object("opts_add_button").show()
            self.builder.get_object("opts_apply_button").hide()
            self.item_id = None
        self.item_index = item_index

        self.load_options(options)
        self.dialog.run()
        self.dialog.destroy()

    def load_options(self, options):
        if options:
            self.builder.get_object("tracker_entry").get_buffer().set_text(options.get("url", ""))

    def in_store(self, item):
        for row in self.gtkui.store:
            if row[0] == item:
                return True
        return False

    def on_add(self, widget):
        try:
            options = self.generate_opts()
            for url in options["urls"]:
                if not self.in_store(url):
                    self.gtkui.store.append([url])
                    self.gtkui.trackers.append({"url": url})
            self.dialog.response(Gtk.ResponseType.DELETE_EVENT)
        except Exception as err:
            dialogs.ErrorDialog("Error", str(err), self.dialog).run()

    def generate_opts(self):
        # generate options dict based on gtk objects
        buffer = self.builder.get_object("tracker_entry").get_buffer()
        options = {
            "urls": buffer.get_text(*buffer.get_bounds(), False).split(),
        }
        if len(options["urls"]) == 0:
            raise Exception("no URLs")
        return options

    def on_apply(self, widget):
        try:
            options = self.generate_opts()
            self.gtkui.store[self.item_id][0] = options["urls"][0]
            self.gtkui.trackers[self.item_index]["url"] = options["urls"][0]
            self.dialog.response(Gtk.ResponseType.DELETE_EVENT)
        except Exception as err:
            dialogs.ErrorDialog("Error", str(err), self.dialog).run()

    def on_cancel(self, widget):
        self.dialog.response(Gtk.ResponseType.DELETE_EVENT)

class Gtk3UI(Gtk3PluginBase):
    def enable(self):
        self.builder = Gtk.Builder.new_from_file(get_resource("config.ui"))
        self.builder.connect_signals({
            "on_add_button_clicked": self.on_add_button_clicked,
            "on_edit_button_clicked": self.on_edit_button_clicked,
            "on_remove_button_clicked": self.on_remove_button_clicked,
            "on_up_button_clicked": self.on_up_button_clicked,
            "on_down_button_clicked": self.on_down_button_clicked,
            "on_reload_now_clicked": self.on_reload_now_clicked,
        })

        component.get("Preferences").add_page("Default Trackers", self.builder.get_object("prefs_box"))
        component.get("PluginManager").register_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").register_hook("on_show_prefs", self.on_show_prefs)

        self.trackers = []
        scrolled_window = self.builder.get_object("scrolledwindow1")
        self.store = self.create_model()
        self.tree_view = Gtk.TreeView(self.store)
        tree_selection = self.tree_view.get_selection()
        tree_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.tree_view.connect("cursor-changed", self.on_listitem_activated)
        self.tree_view.connect("row-activated", self.on_edit_button_clicked)
        self.tree_view.set_rules_hint(True)
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("URL", rendererText, text=0)
        self.tree_view.append_column(column)
        scrolled_window.add(self.tree_view)
        scrolled_window.show_all()

        self.opts_dialog = OptionsDialog(self)

    def disable(self):
        component.get("Preferences").remove_page("Default Trackers")
        component.get("PluginManager").deregister_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").deregister_hook("on_show_prefs", self.on_show_prefs)

    def on_apply_prefs(self):
        log.debug("applying prefs for DefaultTrackers")
        try:
            update_interval = int(self.builder.get_object("tracker_list_update_interval").get_text() or 1)
        except:
            update_interval = 1
        tracker_list_buffer = self.builder.get_object("tracker_list_url").get_buffer()
        start_iter, end_iter = tracker_list_buffer.get_bounds()
        tracker_list_text = tracker_list_buffer.get_text(start_iter, end_iter, False)
        self.config.update({
            "trackers": [{"url": str(row[0])} for row in self.store],
            "dynamic_trackerlist_url": tracker_list_text,
            "dynamic_trackers_update_interval": update_interval,
        })
        client.defaulttrackers.set_config(self.config)

    def on_show_prefs(self):
        client.defaulttrackers.get_config().addCallback(self.cb_get_config)

    def cb_get_config(self, config):
        "callback for on show_prefs"
        self.config = config
        # dynamic tracker list
        if config["dynamic_trackerlist_url"]:
            self.builder.get_object("tracker_list_url").get_buffer().set_text(config["dynamic_trackerlist_url"])
        self.builder.get_object("tracker_list_update_interval").set_text(str(config["dynamic_trackers_update_interval"]))
        # trackers
        self.trackers = list(config["trackers"])
        self.store.clear()
        for tracker in self.trackers:
            self.store.append([tracker["url"]])
        # Workaround for cached builder signal appearing when re-enabling plugin in same session
        if self.builder.get_object("edit_button"):
            # Disable the remove and edit buttons, because nothing in the store is selected
            self.builder.get_object("remove_button").set_sensitive(False)
            self.builder.get_object("edit_button").set_sensitive(False)
            self.builder.get_object("up_button").set_sensitive(False)
            self.builder.get_object("down_button").set_sensitive(False)

    def create_model(self):
        store = Gtk.ListStore(str)
        for tracker in self.trackers:
            store.append([tracker["url"]])
        return store

    def on_listitem_activated(self, treeview):
        tree, tree_paths = self.tree_view.get_selection().get_selected_rows()
        if tree_paths:
            self.builder.get_object("edit_button").set_sensitive(True)
            self.builder.get_object("remove_button").set_sensitive(True)
            self.builder.get_object("up_button").set_sensitive(True)
            self.builder.get_object("down_button").set_sensitive(True)
        else:
            self.builder.get_object("edit_button").set_sensitive(False)
            self.builder.get_object("remove_button").set_sensitive(False)
            self.builder.get_object("up_button").set_sensitive(False)
            self.builder.get_object("down_button").set_sensitive(False)

    def on_add_button_clicked(self, widget):
        self.opts_dialog.show()

    def on_remove_button_clicked(self, widget):
        tree, tree_paths = self.tree_view.get_selection().get_selected_rows()
        to_remove = []
        for tree_path in tree_paths:
            tree_id = tree.get_iter(tree_path)
            index = tree_path[0]
            to_remove.append((index, tree_id))
        for index, tree_id in sorted(to_remove, reverse=True):
            # we need to delete the indices in reverse order to avoid offsets
            del self.trackers[index]
            self.store.remove(tree_id)

    def on_edit_button_clicked(self, widget):
        tree, tree_paths = self.tree_view.get_selection().get_selected_rows()
        if tree_paths:
            tree_path = tree_paths[0]
            tree_id = tree.get_iter(tree_path)
            index = tree_path[0]
            url = str(self.store.get_value(tree_id, 0))
            if url:
                self.opts_dialog.show({
                    "url": url,
                }, tree_id, index)

    def on_up_button_clicked(self, widget):
        tree, tree_paths = self.tree_view.get_selection().get_selected_rows()
        if tree_paths:
            tree_path = tree_paths[0]
            tree_id = tree.get_iter(tree_path)
            prev = iter_prev(tree_id, self.store)
            if prev is not None:
                self.store.swap(prev, tree_id)

    def on_down_button_clicked(self, widget):
        tree, tree_paths = self.tree_view.get_selection().get_selected_rows()
        if tree_paths:
            tree_path = tree_paths[0]
            tree_id = tree.get_iter(tree_path)
            nexti = self.store.iter_next(tree_id)
            if nexti is not None:
                self.store.swap(tree_id, nexti)

    def on_reload_now_clicked(self, widget):
        # reset the last update timestamp
        self.config["last_dynamic_trackers_update"] = 0
        self.on_apply_prefs()
        # we need to reload the tracker list after the update
        client.defaulttrackers.update_trackerlist_from_url().addCallback(self.cb_get_config)

