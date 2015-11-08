## Description

This is a [Deluge][1] plugin that allows you to create a list of default trackers
that will be added to new torrents (and old ones after restarting Deluge). The
plugin will not duplicate existing trackers and does not care how the torrent
was added so it works perfectly fine with infohashes.

Don't use this plugin if you have private torrents where the details are not
supposed to reach public trackers.

## Installation

* create the egg with

    `python setup.py bdist_egg`

(or try to use the one from the [egg][2] directory - be careful to install the py2.7 version of Deluge, http://download.deluge-torrent.org/windows/py2.7/ if you're using Windows)

* add it to Deluge from Preferences -> Plugins -> Install Plugin

## TODO:

* log the added trackers so we can remove them from torrents when they are deleted from the default list
* WebUI version

[1]: http://deluge-torrent.org/
[2]: egg/

