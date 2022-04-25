/*
Script: defaulttrackers.js
    The client-side javascript code for the DefaultTrackers plugin.

Copyright:
    (C) Ștefan Talpalaru 2013-2022 <stefantalpalaru@yahoo.com>
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, write to:
        The Free Software Foundation, Inc.,
        51 Franklin Street, Fifth Floor
        Boston, MA  02110-1301, USA.

    In addition, as a special exception, the copyright holders give
    permission to link the code of portions of this program with the OpenSSL
    library.
    You must obey the GNU General Public License in all respects for all of
    the code used other than OpenSSL. If you modify file(s) with this
    exception, you may extend this exception to your version of the file(s),
    but you are not obligated to do so. If you do not wish to do so, delete
    this exception statement from your version. If you delete this exception
    statement from all source files in the program, then also delete it here.
*/

DefaultTrackersPanel = Ext.extend(Ext.form.FormPanel, {
    constructor: function(config) {
        config = Ext.apply({
            border: false,
            title: ("Default Trackers"),
            autoHeight: true,
        }, config);
        DefaultTrackersPanel.superclass.constructor.call(this, config);
    },
    initComponent: function() {
        DefaultTrackersPanel.superclass.initComponent.call(this);
        this.opts = new Deluge.OptionsManager();

        var fieldset = this.add({
            xtype: 'fieldset',
            title: ('Dynamic tracker list (optional)'),
            autoHeight: true,
            autoWidth: true,
        });
        this.opts.bind('dynamic_trackerlist_url', fieldset.add({
            xtype: 'textarea',
            fieldLabel: ('tracker list URL'),
            anchor: '100%',
            name: 'dynamic_trackerlist_url',
            autoWidth: true,
        }));
        fieldset.add({
            xtype: 'displayfield',
            fieldLabel: 'E.g.',
            value: 'https://newtrackon.com/api/stable or<br>https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt',
        });
        this.opts.bind('dynamic_trackers_update_interval', fieldset.add({
            xtype: 'textfield',
            fieldLabel: ('reload every X days'),
            anchor: '100%',
            name: 'dynamic_trackers_update_interval',
            autoWidth: true,
        }));

        fieldset = this.add({
            xtype: 'fieldset',
            title: ('Default trackers'),
            autoHeight: true,
            autoWidth: true,
        });
        this.opts.bind('trackers_ta', fieldset.add({
            xtype: 'textarea',
            fieldLabel: (''),
            anchor: '100%',
            name: 'trackers_ta',
            height: '200px',
            autoWidth: true,
        }));

        deluge.preferences.on('show', this.onPreferencesShow, this);
    },

    onPreferencesShow: function() {
        deluge.client.defaulttrackers.get_config({
            success: function(config) {
                config.trackers_ta = config.trackers
                    .map(function(tracker){return tracker.url})
                    .join('\n');

                this.opts.set(config);
            },
            scope: this,
        });
    },
    onApply: function(e) {
        var changed = this.opts.getDirty();
        if (!Ext.isObjectEmpty(changed)) {
            if (Ext.isDefined(changed['trackers_ta'])) {
                changed.trackers = changed.trackers_ta
                    .split('\n')
                    .filter(function(line){return line != ''})
                    .map(function(url){return {'url': url}});
            }

            deluge.client.defaulttrackers.set_config(changed, {
                success: this.onSetConfig,
                scope: this,
            });
        }
    },
    onSetConfig: function() {
        this.opts.commit();
    },
});

DefaultTrackersPlugin = Ext.extend(Deluge.Plugin, {
    name: "Default Trackers",

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = new DefaultTrackersPanel();
        this.prefsPage = deluge.preferences.addPage(this.prefsPage);
    }
});

Deluge.registerPlugin("Default Trackers", DefaultTrackersPlugin);
