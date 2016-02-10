#
# core.py
#
# Copyright (C) 2013-2015 Stefan Talpalaru <stefantalpalaru@yahoo.com>
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

import logging
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from pprint import pprint

DEFAULT_PREFS = {
    "trackers": [
        #{"url": "test"},
    ],
}

log = logging.getLogger(__name__)

class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager("defaulttrackers.conf", DEFAULT_PREFS)
        component.get("EventManager").register_event_handler(
            "TorrentAddedEvent", self.on_torrent_added
        )

    def disable(self):
        component.get("EventManager").deregister_event_handler(
            "TorrentAddedEvent", self.on_torrent_added
        )

    def update(self):
        pass

    def on_torrent_added(self, torrent_id):
        torrent = component.get("TorrentManager")[torrent_id]
        if torrent.torrent_info.priv() or torrent.get_status(["private"])["private"]:
            return
        trackers = torrent.get_status(["trackers"])["trackers"]
        existing_urls = [tracker["url"] for tracker in trackers]
        got_new_trackers = False
        for new_tracker in self.config["trackers"]:
            if new_tracker["url"] not in existing_urls:
                got_new_trackers = True
                trackers.append({
                    "tier": 0,
                    "url": str(new_tracker["url"]),
                })
        if got_new_trackers:
            torrent.set_trackers(trackers)
            log.debug("added new trackers for %s" % torrent.filename)

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config

