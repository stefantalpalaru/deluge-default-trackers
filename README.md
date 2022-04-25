## Description

This is a [Deluge][1] plugin that allows you to create a list of default trackers
that will be added to new public torrents (and old ones after restarting Deluge). The
plugin will not duplicate existing trackers and does not care how the torrent
was added so it works perfectly fine with infohashes.

Private torrents are excluded on purpose, because their metadata is not
supposed to reach public trackers.

Besides manually creating the default tracker list, you can also load it (periodically) from a URL.

This plugin is compatible with Deluge 2.0 and Python 3.6+.

## Installation

* create the egg with

    `python setup.py bdist_egg`

(or try to use [the one from the "egg" directory][2] - rename it, if it doesn't match your Python3 version)

* you need to use the same version of Python3 as the one that Deluge is running under.

* add it to Deluge from Preferences -> Plugins -> Install Plugin

* now you can go to Preferences -> Default Trackers and add individual default trackers, or the URL of a list that should be periodically downloaded
  (e.g.: https://newtrackon.com/api/stable
or https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt)

## Troubleshooting

To get Deluge's output on Windows, run this in a terminal ("cmd" works):

`"%ProgramFiles%\Deluge\deluge-debug.exe"`

## TODO:

* log the added trackers so we can remove them from torrents when they are deleted from the default list

[1]: http://deluge-torrent.org/
[2]: https://github.com/stefantalpalaru/deluge-default-trackers/raw/master/egg

