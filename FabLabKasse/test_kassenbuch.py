#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# FabLabKasse, a Point-of-Sale Software for FabLabs and other public and trust-based workshops.
# Copyright (C) 2015  Patrick Kanzler <patrick.kanzler@fablab.fau.de>
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
"""unittests for kassenbuch.py"""
import unittest
from FabLabKasse.kassenbuch import Kasse, Kunde, NoDataFound
from hypothesis import given
from hypothesis.strategies import text


class KassenbuchTestCase(unittest.TestCase):
    """unittests for kassenbuch.py"""
    def test_accounting_database_setup(self):
        """tests the creation of the accounting database"""
        kasse = Kasse(sqlite_file=':memory:')
        kasse.con.commit()
        # TODO check the database instead of the functions of Kasse
        self.assertFalse(kasse.kunden)
        self.assertFalse(kasse.rechnungen)
        self.assertFalse(kasse.buchungen)

    @given(clientname=text())
    def test_accounting_database_client_creation(self, clientname):
        """very basically test the creation of a new client"""
        kasse = Kasse(sqlite_file=':memory:')
        self.assertFalse(kasse.kunden)
        # TODO thouroughly test client creation, this seems to be fishy somewhere
        bob = Kunde(clientname, schuldengrenze=0)
        bob.store(cur=kasse.cur)
        kasse.con.commit()
        try:
            Kunde.load_from_name(clientname, kasse.cur)
        except NoDataFound:
            self.fail("client entry in database has not been created")
        # TODO test integrity checking (no double creation of same ID)
        # TODO code crashes when reading Kunde with "None" in e.g. schuldengrenze