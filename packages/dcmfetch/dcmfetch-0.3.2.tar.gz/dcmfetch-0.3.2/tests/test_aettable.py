#!/usr/bin/env python
import unittest
import os
import sys
from os.path import join, dirname, abspath
from tempfile import mkdtemp
from shutil import rmtree

TESTDIR = dirname(abspath(__file__))
sys.path.insert(0, abspath(join(TESTDIR, '..')))

import dcmfetch.aettable as aettable

NODEFILE0 = '''#
# dicom nodes for  web interface
#
CRIC CRICStore canopus 11112 FGX
Dcm4Chee CRICStore canopus 11112 FGX
'''

NODEFILE1 = '''#
CRIC
'''

NODEFILE2 = '''#
CRIC CRICStore canopus xxxx FGX
'''

NODEFILE3 = '''#
CRIC CRICStore canopus 104 ZZZ
'''

NODEFILE4 = '''#
WEB dcm-web/base canopus 8080 W user:passwd
'''

NODEFILE5 = '''#
WEBS dcm-web/base canopus 443 WS user:passwd
'''

class TestAetTable(unittest.TestCase):
    ''' Tests for functions in aettable.py '''

    @classmethod
    def setUpClass(cls):
        cls._olcwd = os.getcwd()
        cls._tmpwd = mkdtemp()
        os.chdir(cls._tmpwd)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._olcwd)
        rmtree(cls._tmpwd)

    def test_nofile(self):
        with self.assertRaises(IOError):
            aettable.AetTable('NOSUCHFILE')

    def test_aettable0(self):
        with open('nodes.cf', 'w') as f:
            f.write(NODEFILE0)
        tbl = aettable.AetTable('nodes.cf')
        self.assertEqual(len(tbl), 2)
        self.assertEqual(list(tbl.keys())[0], 'CRIC')
        self.assertEqual(
            tbl['CRIC'],
            aettable.AetEntry('CRICStore', 'canopus', 11112, 'FGX', None, None, None, None)
        )

    def test_aettable1(self):
        with open('nodes.cf', 'w') as f:
            f.write(NODEFILE1)
        tbl = aettable.AetTable('nodes.cf')
        self.assertEqual(len(tbl), 0)

    def test_aettable2(self):
        with open('nodes.cf', 'w') as f:
            f.write(NODEFILE2)
        tbl = aettable.AetTable('nodes.cf')
        self.assertEqual(len(tbl), 0)

    def test_aettable3(self):
        with open('nodes.cf', 'w') as f:
            f.write(NODEFILE3)
        tbl = aettable.AetTable('nodes.cf')
        self.assertEqual(len(tbl), 0)

    def test_aettable4(self):
        with open('nodes.cf', 'w') as f:
            f.write(NODEFILE4)
        tbl = aettable.AetTable('nodes.cf')
        self.assertEqual(len(tbl), 1)
        self.assertEqual(list(tbl.keys())[0], 'WEB')
        self.assertEqual(
            tbl['WEB'],
            aettable.AetEntry('dcm-web/base', 'canopus', 8080, 'W', None, None, 'user:passwd', 'http')
        )

    def test_aettable5(self):
        with open('nodes.cf', 'w') as f:
            f.write(NODEFILE5)
        tbl = aettable.AetTable('nodes.cf')
        self.assertEqual(len(tbl), 1)
        self.assertEqual(list(tbl.keys())[0], 'WEBS')
        self.assertEqual(
            tbl['WEBS'],
            aettable.AetEntry('dcm-web/base', 'canopus', 443, 'WS', None, None, 'user:passwd', 'https')
        )

    def tearDown(self):
        try:
            os.unlink('nodes.cf')
        except OSError:
            pass


if __name__ == '__main__':
    unittest.main()
