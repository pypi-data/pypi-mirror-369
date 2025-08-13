import unittest
import os
import sys
from tempfile import mkdtemp
from glob import glob
from shutil import rmtree
from os.path import join, dirname, abspath
from subprocess import Popen, STDOUT, DEVNULL
from time import sleep

from pydicom import dcmread


TESTDIR = dirname(abspath(__file__))
sys.path.insert(0, abspath(join(TESTDIR, '..')))
TESTDATA = join(TESTDIR, 'testdata')

from dcmfetch.dcmfetch import *
from dcmfetch.dcmfetch import _filter_by_date

SRVPROG = 'dcmqrscp'
SRVARGS = ['--no-storage', '-b', 'DCMQRSCP:11112', '--dicomdir', join(TESTDATA, 'DICOMDIR')]
os.environ['PATH'] = os.pathsep.join([TESTDIR] + os.environ['PATH'].split(os.pathsep))

NODEFILE = '''
Server DCMQRSCP localhost 11112 FSGX
'''

PATID = 'PQA20160906RHD'
STUDYUID = '1.3.12.2.1107.5.2.19.45064.30000016090616040707700000004'
SERIESUID = '1.3.12.2.1107.5.2.19.45064.2016090617560117683773517.0.0.0'

PATID_B = 'QQA20180418BCHSKYRA'
STUDYUID_B = '1.3.12.2.1107.5.2.19.45622.30000018041807565753300000009'
SERIESUID_B1 = '1.3.12.2.1107.5.2.19.45622.201804181719501256341027.0.0.0'
SERIESUID_B2 = '1.3.12.2.1107.5.2.19.45622.2018041817462338771353016.0.0.0'

NIMAGES = 3


class TestDcmFetch(unittest.TestCase):
    """Tests for functions in dicomweb.py"""
    @classmethod
    def setUpClass(cls):
        cls._process = Popen([SRVPROG] + SRVARGS, stdout=DEVNULL, stderr=STDOUT)
        sleep(1)
        cls._olcwd = os.getcwd()
        cls._tmpwd = mkdtemp()
        os.chdir(cls._tmpwd)
        with open('dcmnodes.cf', 'w') as f:
            f.write(NODEFILE)

    @classmethod
    def tearDownClass(cls):
        cls._process.terminate()
        cls._process.wait()
        os.chdir(cls._olcwd)
        rmtree(cls._tmpwd)

    def test_fetch_series(self):
        dobjs = fetch_series(PATID, stuid='1', sernos=1, server='Server')
        assert len(dobjs) == NIMAGES
        assert all(d.PatientID == PATID for d in dobjs)

    def test_fetch_series_2(self):
        '''check multiple series don't interfere with each other'''
        dobjs = fetch_series(PATID_B, stuid='1', sernos=[1, 14], server='Server')
        assert len(dobjs) == 2*NIMAGES, '%d' % len(dobjs)
        assert all(d.PatientID == PATID_B for d in dobjs)
        assert all(d.StudyInstanceUID == STUDYUID_B for d in dobjs)
        assert set(d.SeriesInstanceUID for d in dobjs) == set([SERIESUID_B1, SERIESUID_B2])

    def test__filter_by_date(self):
        dobjs = [dcmread(f) for f in glob(join(TESTDATA, 'MR*'))]

        self.assertEqual(len(dobjs), 9)
        self.assertEqual(len(sorted(set(d.StudyDate for d in dobjs))), 2)
        self.assertEqual(len(_filter_by_date(dobjs)), len(dobjs))
        self.assertEqual(len(_filter_by_date(dobjs, 'all')), len(dobjs))

        self.assertEqual(len(_filter_by_date(dobjs, 'earliest')), 3)
        self.assertEqual(len(set(d.StudyDate for d in _filter_by_date(dobjs, 'first'))), 1)
        self.assertEqual(_filter_by_date(dobjs, 'earliest')[0].StudyDate,  '20160906')

        self.assertEqual(len(_filter_by_date(dobjs, 'latest')), 6)
        self.assertEqual(len(set(d.StudyDate for d in _filter_by_date(dobjs, 'last'))), 1)
        self.assertEqual(_filter_by_date(dobjs, 'latest')[0].StudyDate, '20180418')

        self.assertEqual(len(_filter_by_date(dobjs, '20160101')), 3)
        self.assertEqual(len(set(d.StudyDate for d in _filter_by_date(dobjs, '20160101'))), 1)
        self.assertEqual(_filter_by_date(dobjs, '20160101')[0].StudyDate, '20160906')

        self.assertEqual(len(_filter_by_date(dobjs, '20170101')), 3)
        self.assertEqual(len(set(d.StudyDate for d in _filter_by_date(dobjs, '20170101'))), 1)
        self.assertEqual(_filter_by_date(dobjs, '20170101')[0].StudyDate, '20160906')

        self.assertEqual(len(_filter_by_date(dobjs, '20171231')), 6)
        self.assertEqual(len(set(d.StudyDate for d in _filter_by_date(dobjs, '20171231'))), 1)
        self.assertEqual(_filter_by_date(dobjs, '20171231')[0].StudyDate, '20180418')

        self.assertEqual(len(_filter_by_date(dobjs, '20181231')), 6)
        self.assertEqual(len(set(d.StudyDate for d in _filter_by_date(dobjs, '20181231'))), 1)
        self.assertEqual(_filter_by_date(dobjs, '20181231')[0].StudyDate, '20180418')

        with self.assertRaises(ValueError):
            _filter_by_date(dobjs, '')

        with self.assertRaises(ValueError):
            _filter_by_date(dobjs, ' ')

        with self.assertRaises(ValueError):
            _filter_by_date(dobjs, '20180229')


    def test_fetch_series_to_disk(self):
        tempd = mkdtemp()
        nser = fetch_series_to_disk(
            PATID, outdir=tempd,
            studyid='1', sernos=1, server='Server', usezip=False
        )
        assert nser == 1

        dir_ = glob(join(tempd, '*'))[0]
        nfound = len(glob(join(dir_, '*')))
        assert nfound == NIMAGES

        dobjs = read_series(dir_, key=None, numeric=False, reverse=False, globspec='*')
        assert len(dobjs) == NIMAGES, '%d' % len(dobjs)

        rmtree(tempd)


if __name__ == '__main__':
    unittest.main()
