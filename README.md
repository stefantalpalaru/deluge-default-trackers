## Description

This is a [Deluge][1] plugin that allows you to create a list of default trackers
that will be added to new public torrents (and old ones after restarting Deluge). The
plugin will not duplicate existing trackers and does not care how the torrent
was added so it works perfectly fine with infohashes.

Private torrents are excluded on purpose, because their metadata is not
supposed to reach public trackers.

Besides manually creating the default tracker list, you can also load it (periodically) from a URL.

## Installation

* create the egg with

    `python setup.py bdist_egg`

(or try to use the one from the [egg][2] directory - be careful to install the py2.7 version of Deluge, if you're using Windows)

* add it to Deluge from Preferences -> Plugins -> Install Plugin

## Troubleshooting

To get Deluge's output on Windows, run this in a terminal ("cmd" works):

`"%ProgramFiles%\Deluge\deluge-debug.exe"`

## TODO:

* log the added trackers so we can remove them from torrents when they are deleted from the default list
* WebUI version

[1]: http://deluge-torrent.org/
[2]: egg/

