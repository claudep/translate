#!/usr/bin/env python

from translate.misc import wStringIO
from translate.storage import test_monolingual, txt


class TestTxtUnit(test_monolingual.TestMonolingualUnit):
    UnitClass = txt.TxtUnit


class TestTxtFile(test_monolingual.TestMonolingualStore):
    StoreClass = txt.TxtFile

    def txtparse(self, txtsource):
        """helper that parses txt source without requiring files"""
        dummyfile = wStringIO.StringIO(txtsource)
        txtfile = self.StoreClass(dummyfile)
        return txtfile

    def txtregen(self, txtsource):
        """helper that converts txt source to txtfile object and back"""
        return self.txtparse(txtsource).serialize()

    def test_simpleblock(self):
        """checks that a simple txt block is parsed correctly"""
        txtsource = 'bananas for sale'
        txtfile = self.txtparse(txtsource)
        assert len(txtfile.units) == 1
        assert txtfile.units[0].source == txtsource
        assert self.txtregen(txtsource) == txtsource

    def test_multipleblocks(self):
        """ check that multiple blocks are parsed correctly"""
        txtsource = '''One\nOne\n\nTwo\n---\n\nThree'''
        txtfile = self.txtparse(txtsource)
        assert len(txtfile.units) == 3
        print(txtsource)
        print(txtfile.serialize())
        print("*%s*" % txtfile.units[0])
        assert txtfile.serialize() == txtsource
        assert self.txtregen(txtsource) == txtsource
