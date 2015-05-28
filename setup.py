#!python2
# Force Python to compile with 2.x when 3.x is also present on dev system.
#
# setup.py
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

from setuptools import setup, find_packages

__plugin_name__ = "DefaultTrackers"
__author__ = "Stefan Talpalaru"
__author_email__ = "stefantalpalaru@yahoo.com"
__version__ = "0.1"
__url__ = "https://github.com/stefantalpalaru/deluge-default-trackers"
__license__ = "GPLv3"
__description__ = "Add a list of default trackers to all the torrents"
__long_description__ = """
Create a list of default trackers that will be added to new torrents (and old
ones after restarting Deluge). The plugin will not duplicate existing trackers
and does not care how the torrent was added so it works perfectly fine with
infohashes.

Don't use this plugin if you have private torrents where the details are not
supposed to reach public trackers.
"""
__pkg_data__ = {__plugin_name__.lower(): ["data/*"]}

setup(
    name=__plugin_name__,
    version=__version__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__license__,
    long_description=__long_description__ if __long_description__ else __description__,

    packages=[__plugin_name__.lower()],
    package_data = __pkg_data__,

    entry_points="""
    [deluge.plugin.core]
    %(plugin_name)s = %(plugin_module)s:CorePlugin
    [deluge.plugin.gtkui]
    %(plugin_name)s = %(plugin_module)s:GtkUIPlugin
    [deluge.plugin.web]
    %(plugin_name)s = %(plugin_module)s:WebUIPlugin
    """ % dict(plugin_name=__plugin_name__, plugin_module=__plugin_name__.lower())
)
