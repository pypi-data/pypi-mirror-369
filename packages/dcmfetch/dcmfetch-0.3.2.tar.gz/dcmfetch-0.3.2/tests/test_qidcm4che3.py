import unittest
import os
import sys
import tempfile
from glob import glob
from os.path import join, abspath, dirname
from shutil import rmtree
from subprocess import Popen, STDOUT, DEVNULL
from time import sleep

from pydicom import dcmread

PATID = 'PQA20160906RHD'
STUDYUID = '1.3.12.2.1107.5.2.19.45064.30000016090616040707700000004'
SERIESUID = '1.3.12.2.1107.5.2.19.45064.2016090617560117683773517.0.0.0'
IMAGEUID = '1.3.12.2.1107.5.2.19.45064.2016090617561210676173525'
NIMAGES = 3
INSTANCENUMBER = 1

AET = 'DCMQRSCP'
NODE = 'localhost'
PORT = 11112
LAET = 'QRSCU'

TESTDIR = dirname(abspath(__file__))
sys.path.insert(0, abspath(join(TESTDIR, '..')))
TESTDATA = join(TESTDIR, 'testdata')

from dcmfetch.qidcm4che3 import *

SRVPROG = join(TESTDIR, 'dcmqrscp.exe' if os.name == 'nt' else 'dcmqrscp')
SRVARGS = ['--no-storage', '-b', 'DCMQRSCP:11112', '--dicomdir', join(TESTDATA, 'DICOMDIR')]


class TestQIDcm4Che3(unittest.TestCase):
    """Tests for functions in qidcm4che3.py"""

    @classmethod
    def setUpClass(cls):
        cls._process = Popen([SRVPROG] + SRVARGS, stdout=DEVNULL, stderr=STDOUT)
        sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls._process.terminate()
        cls._process.wait()

    def test_dcm_pat_level_find(self):
        patients = dcm_pat_level_find(
            aet=AET, node=NODE, port=PORT, laet=LAET,
            patname='', patid=PATID, birthdate='', sex=''
        )
        self.assertEqual(patients[0].patid, PATID)

    def test_dcm_stu_level_find(self):
        studies = dcm_stu_level_find(
            aet=AET, node=NODE, port=PORT, laet=LAET,
            patid=PATID
        )
        self.assertEqual(studies[0].studyuid, STUDYUID)

    def test_dcm_ser_level_find(self):
        series = dcm_ser_level_find(
            aet=AET, node=NODE, port=PORT, laet=LAET,
            patid=PATID, studyuid=STUDYUID
        )
        self.assertEqual(series[0].seriesuid, SERIESUID)

    def test_dcm_img_level_find(self):
        images = dcm_img_level_find(
            aet=AET, node=NODE, port=PORT, laet=LAET,
            patid=PATID, studyuid=STUDYUID, seriesuid=SERIESUID
        )
        self.assertEqual(len(images), NIMAGES)
        images = sorted(images, key=lambda x: x.imagenumber)
        self.assertEqual(images[0].imageuid, IMAGEUID)

    def test_dcm_ser_level_get(self):
        tempd = tempfile.mkdtemp()
        fetch_iter = dcm_ser_level_get(
            aet=AET, node=NODE, port=PORT, laet=LAET,
            patid=PATID, studyuid=STUDYUID, seriesuid=SERIESUID,
            savedir=tempd)
        list(fetch_iter)

        dobjs = sorted(
            [dcmread(f) for f in glob(join(tempd, '*'))],
            key=lambda d: int(d.InstanceNumber)
        )
        self.assertEqual(len([int(d.InstanceNumber) for d in dobjs]), NIMAGES)
        rmtree(tempd)

    def test_dcm_img_level_get(self):
        tempd = tempfile.mkdtemp()
        fetch_iter = dcm_img_level_get(
            aet=AET, node=NODE, port=PORT, laet=LAET,
            patid=PATID, studyuid=STUDYUID, seriesuid=SERIESUID, imageuid=IMAGEUID,
            savedir=tempd)
        list(fetch_iter)

        dobjs = sorted(
            [dcmread(f) for f in glob(join(tempd, '*'))],
            key=lambda d: int(d.InstanceNumber)
        )
        self.assertEqual(len(dobjs), 1)
        self.assertEqual(dobjs[0].InstanceNumber, INSTANCENUMBER)
        rmtree(tempd)


if __name__ == '__main__':
    unittest.main()
