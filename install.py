#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   eLyXer -- convert LyX source files to HTML output.
#
#   Copyright (C) 2009 Alex Fernández
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# --end--
# eLyXer multi-platform installation (modernized for Python 3)

import platform
import sys
import os
import shutil
import gettext


class Installer:
    "The eLyXer installer."

    elyxer = 'elyxer.py'
    separators = {'Linux': ':', 'Windows': ';', 'Darwin': ':'}
    preferredstarts = ['/usr/bin', 'c:\\windows\\system', '/usr/local/bin']

    def error(self, string):
        "Print an error string."
        self.show(string, sys.stderr)

    def show(self, message, channel=sys.stdout):
        "Show a message out of a channel."
        channel.write(message + '\n')

    def usage(self):
        "Show usage and requirements."
        self.error('Usage: python3 install.py')
        self.error('Requirements: Python 3.6 or later.')
        sys.exit(1)

    def copybin(self):
        "Check permissions, try to copy binary file to any system path."
        for path in self.sortpaths():
            try:
                shutil.copy2(Installer.elyxer, path)
                self.show('eLyXer installed as a binary in ' + path)
                self.show('Please run as "elyxer.py [options] input.lyx output.html" to use it')
                return
            except OSError:
                pass
        self.error('eLyXer not installed into PATH')

    def sortpaths(self):
        "Sort PATH, placing paths containing python first and stripping current dir."
        system = platform.system()
        if system not in Installer.separators:
            self.error('Unknown operating system ' + system + '; aborting')
            self.usage()
        separator = Installer.separators[system]
        paths = os.environ.get('PATH', '').split(separator)
        withpython = []
        preferred = []
        rest = []
        while paths:
            path = paths.pop()
            if 'python' in path.lower():
                withpython.append(path)
            elif self.ispreferred(path):
                preferred.append(path)
            elif path and path != '.':
                rest.append(path + '/')
        return withpython + preferred + rest

    def ispreferred(self, path):
        "Find out if the path starts with one of the preferred paths."
        for preferredstart in Installer.preferredstarts:
            if path.lower().startswith(preferredstart):
                return True
        return False

    def installmodule(self):
        "Install eLyXer as a Python package using pip."
        if not self.checkpermissions('install as a Python module'):
            return
        res = os.system(f'"{sys.executable}" -m pip install .')
        if res == 0:
            self.show('eLyXer installed as a module.')
            self.show('You can also run eLyXer as "python3 -m elyxer [options] input.lyx output.html"')
        else:
            self.error('Failed to install eLyXer via pip.')

    def installtranslations(self):
        "Install the translation files."
        destination = gettext.bindtextdomain('elyxer')
        if destination and os.path.isdir('po/locale'):
            self.copy('po/locale', destination)

    def copy(self, source, destination):
        "Recursively copy a file or directory into another."
        if not self.checkpermissions('install translation modules'):
            return
        if os.path.isfile(source):
            shutil.copy2(source, destination)
            return
        if not os.path.exists(destination):
            shutil.copytree(source, destination)
            return
        for filename in os.listdir(source):
            self.copy(os.path.join(source, filename), os.path.join(destination, filename))

    def checkpermissions(self, purpose):
        "Check if the user has permissions as root to do something."
        if platform.system() == 'Linux':
            if os.geteuid() != 0:
                self.error('Need to be root to ' + purpose)
                return False
        return True

    def checkversion(self):
        "Check the current version and run installation."
        if sys.version_info < (3, 6):
            self.error(f'Invalid Python version {sys.version.split()[0]}')
            self.usage()
        self.installmodule()
        self.installtranslations()


if __name__ == '__main__':
    Installer().checkversion()
