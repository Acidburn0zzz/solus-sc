#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import GObject


class PopulationFilter:
    """ A population filter is provided to the provider plugin to begin
        population of a given type
    """

    INSTALLED = 0  # Installed packages
    SEARCH = 1     # Perform a search
    CATEGORY = 2   # List within category
    NEW = 3        # Find new packages
    RECENT = 4     # Find recently updated packages
    FEATURED = 5   # Basically "hot stuff"


class ItemStatus:
    """ The ItemStatus allows us to know the exact state of any given item
        as a combination of the various status flags
    """

    INSTALLED = 1 << 0
    UPDATE_NEEDED = 1 << 1    # We have an update available
    UPDATING = 1 << 2
    REMOVING = 1 << 3
    UPDATE_SECURITY = 1 << 4  # Security update available
    UPDATE_CRITICAL = 1 << 5  # Critical update available
    UPDATE_BUGFIX = 1 << 6    # Bugfix update available
    META_DEVEL = 1 << 7       # Is a development type of package
    META_CHANGELOG = 1 << 8   # Supports changelog functionality
    META_ESSENTIAL = 1 << 9   # Essential component. Do NOT remove!


class ProviderCategory(GObject.Object):
    """ ProviderCategory provides categorisation for the software center and
        allows nesting for the native items """

    __gtype_name__ = "NxProviderCategory"

    def __init__(self):
        GObject.Object.__init__(self)

    def get_id(self):
        """ Get the internal ID for this category """
        raise RuntimeError("implement get_id")

    def get_name(self):
        """ Get the display name for this category """
        raise RuntimeError("implement get_name")

    def get_icon_name(self):
        """ Get a display icon for this category """
        raise RuntimeError("implement get_icon_name")

    def get_children(self):
        """ Get any nested child categories """
        return []


class ProviderSource(GObject.Object):
    """ ProviderSource indicates sources used or available for use by a given
        plugin backend. In native implementations this is invariably a repo.
    """

    __gtype_name__ = "NxProviderSource"

    parent_plugin = None

    def __init__(self):
        GObject.Object.__init__(self)

    def get_name(self):
        """ Return human readable name for this source """
        raise RuntimeError("implement get_name")

    def describe(self):
        """ Request a human readable description for this source """
        raise RuntimeError("implement describe")

    def enable(self):
        """ Request this source be enabled """
        raise RuntimeError("implement enable")

    def disable(self):
        """ Request this source be disabled """
        raise RuntimeError("implement disable")

    def can_edit(self):
        """ Determines whether the source can be edited """
        return False

    def get_plugin(self):
        return self.parent_plugin


class ProviderStorage(GObject.Object):
    """ ProviderStorage is an abstract type that should be populated by
        existing plugins

        Storage may be recycled at any time and is used simply to allow
        dynamic "pushing" of items into the storage
    """

    __gtype_name__ = "NxProviderStorage"

    def __init__(self):
        GObject.Object.__init__(self)

    def add_item(self, id, item, popfilter):
        raise RuntimeError("implement add_item")

    def clear(self):
        raise RuntimeError("implement clear")


class SearchRequest(GObject.Object):
    """ SearchRequest is passed as the extra argument to populate_storage
        to permit controlling the search.
    """

    __gtype_name__ = "ScSearchRequest"

    installed_only = False
    term = None

    def __init__(self, term):
        GObject.Object.__init__(self)
        self.term = term

    def set_installed_only(self, installed_only):
        """ Whether this request is for installed only """
        self.installed_only = installed_only

    def get_installed_only(self):
        return self.installed_only

    def get_term(self):
        return self.term


class ProviderPlugin(GObject.Object):
    """ A ProviderPlugin provides its own managemenet and access to the
        underlying package management system to provide the options to the
        user
    """

    __gtype_name__ = "NxProviderPlugin"

    def __init__(self):
        GObject.Object.__init__(self)

    def populate_storage(self, storage, popfilter, extra):
        """ Populate storage using the given filter """
        raise RuntimeError("implement populate_storage")

    def cancel(self):
        """ Cancel any ongoing populare_storage calls """
        raise RuntimeError("implement cancel")

    def sources(self):
        """ Return the current set of sources for this plugin """
        return []

    def categories(self):
        """ Return the categories known by this plugin """
        return []

    def install_item(self, executor, item):
        raise RuntimeError("implement install_item")

    def remove_item(self, executor, item):
        raise RuntimeError("implement remove_item")

    def upgrade_item(self, executor, item):
        raise RuntimeError("implement upgrade_item")

    def plan_install_item(self, item):
        """ Implementation needs to return a list of all items to be installed
            to satisfy the installation of this item

            Returning an item that IS installed will mark it for removal
        """
        raise RuntimeError("implement plan_install_item")

    def plan_remove_item(self, item):
        """ Implementation needs to return a list of all items to be removed
            to satisfy the removal of this item

            Returning an item that is NOT installed will mark it for install
        """
        raise RuntimeError("implement plan_remove_item")

    def refresh_source(self, executor, source):
        """ Implementation needs to refresh the given source """
        raise RuntimeError("implement refresh_source")


class ProviderItem(GObject.Object):
    """ A ProviderItem is addded to the ProviderStorage by each ProviderPlugin
        and enables access + caching of various backend package management
        systems
    """

    status = None

    parent_plugin = None

    def __init__(self):
        GObject.Object.__init__(self)
        # Default to no status
        self.status = 0

    def get_status(self):
        """ Return the current status for this item """
        return self.status

    def remove_status(self, st):
        """ Remove a status field """
        self.status ^= st

    def add_status(self, st):
        """ Add a status field """
        self.status |= st

    def set_status(self, st):
        """ Set the complete status """
        self.status = st

    def has_status(self, st):
        return self.status & st == st

    def get_id(self):
        """ Every item should return their unique ID so that they can
            be tracked and differentiated between different backends
        """
        raise RuntimeError("implement get_id")

    def get_name(self):
        """ Actual name of the item. Title is stylised separateley """
        raise RuntimeError("implement get_name")

    def get_title(self):
        """ Each item should return an appropriate item for displaying
            as the stylised title
        """
        raise RuntimeError("implement get_title")

    def get_summary(self):
        """ Each item should return a brief summary suitable for single line
            listing of the summary beside the name/version/etc
        """
        raise RuntimeError("implement get_summary")

    def get_description(self):
        """ Each item should support returning their complete description
        """
        raise RuntimeError("implement get_description")

    def get_version(self):
        """ Each item should return a usable version string. This is purely
            for cosmectics
        """
        raise RuntimeError("implement get_version")

    def get_plugin(self):
        return self.parent_plugin
