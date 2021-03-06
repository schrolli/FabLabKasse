#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# FabLabKasse, a Point-of-Sale Software for FabLabs and other public and trust-based workshops.
# Copyright (C) 2014  Julian Hammer <julian.hammer@fablab.fau.de>
#                     Maximilian Gaukler <max@fablab.fau.de>
#                     Timo Voigt <timo@fablab.fau.de>
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
# see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import os
import sys
import subprocess
import time
from FabLabKasse import scriptHelper
import shutil
scriptHelper.setupSigInt()

reallyPrint = print


def print(x):
    sys.stdout.write(x + "\n")
    sys.stdout.flush()


def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


def main():
    currentDir = os.path.dirname(__file__) + "/"
    os.chdir(currentDir)
    currentDir = os.getcwd() + "/"
    os.chdir(currentDir + "/FabLabKasse/")

    if "--example" in sys.argv:
        # load example config
        # test that there is no config.ini yet
        if file_exists("config.ini"):
            print("Warning: Configuration FabLabKasse/config.ini already exists, will not overwrite it.")
            if "--only-load-config" not in sys.argv:
                print("You can just start run.py without the --example argument to make this message disappear.")
                time.sleep(2)
        else:
            print("loading example configuration file. edit FabLabKasse/config.ini to change. You do not need the --example parameter later.")
            shutil.copyfile("config.ini.example", "config.ini")
    if "--only-load-config" in sys.argv:
         # the Vagrant VM provisioning script uses this to copy a default config before the first start.
         sys.exit(0)


    os.chdir(currentDir + "/FabLabKasse/UI/")
    subprocess.call("./compile_all.py")

    os.chdir(currentDir + "/FabLabKasse/")
    # subprocess.call("./importProdukte.py")
    myEnv = dict(os.environ)
    myEnv["LANG"] = "de_DE.UTF-8"
    myEnv["PYTHONIOENCODING"] = "UTF-8"
    myEnv["PYTHONPATH"] = currentDir  # FabLabKasse git folder should be the main module starting point

    cfg = scriptHelper.getConfig()

    if not ('--no-update' in sys.argv):
        # start product import for some offline methods that load from a text file
        print("updating products [use --no-update to skip]")
        if cfg.get("backend", "backend") == "legacy_offline_kassenbuch":
            subprocess.call("./shopping/backend/legacy_offline_kassenbuch_tools/importProdukteOERP.py", env=myEnv)

    def check_winpdb_version():
        """returns true if version of winpdb is larger than 1.4.8

        uses the assumption that winpdb --version returns something like Winpdb 1.4.8 - Tychod

        :return: True, if winpdb-version is sufficient
        :rtype: Boolean
        """
        def versiontuple(v):
            """simple tupel for comparing versions"""
            return tuple(map(int, (v.split("."))))

        # call winpdb --version
        versionstring = subprocess.check_output("winpdb --version", shell=True)
        version = versionstring.split(" ")[1]
        return versiontuple(version) >= versiontuple("1.4.8")

    def runShutdown(program):
        """run sudo <program> and wait forever until the system reboots / shuts down"""
        print("calling {0}".format(program))
        time.sleep(1)
        if subprocess.call(["sudo", program]) != 0:
            print("cannot sudo {0}".format(program))
            time.sleep(5)
        else:
            while True:
                print("Waiting for system {0}".format(program))
                sys.stdout.flush()
                time.sleep(1)

    os.chdir(currentDir + "/FabLabKasse/")
    print("starting GUI")
    debug = ""
    if "--debug" in sys.argv:
        debug = "--debug"
    gui = subprocess.Popen("python2.7 -m FabLabKasse.gui {}".format(debug).split(" "), env=myEnv)
    if debug:
        time.sleep(1)
        if not check_winpdb_version():
            print("WARNING: your version of winpdb is probably not supported")
            print("consider updating winpdb")
        debugger = subprocess.Popen(["winpdb", "-a", os.path.abspath("gui.py")], stdin=subprocess.PIPE)
        debugger.stdin.write("gui")
        debugger.stdin.close()
    gui.communicate()
    print("GUI exited")
    if "--debug" in sys.argv:
        sys.exit(0)
    if os.access("./reboot-now", os.R_OK):
        os.unlink("./reboot-now")
        runShutdown("reboot")
    if os.access("./shutdown-now", os.R_OK):
        os.unlink("./shutdown-now")
        runShutdown("poweroff")

if __name__ == "__main__":
    main()
