#!/usr/bin/env python3
import unittest
from os.path import join, abspath, dirname
import sys

TESTDIR = dirname(abspath(__file__))
sys.path.insert(0, abspath(join(TESTDIR, '..')))

from dcmfetch.structures import (
    PatientLevelFields, StudyLevelFields, SeriesLevelFields,
    ImageLevelFields, ComboFields,
    CGetResponse, CStoreResponse
)


class TestStructures(unittest.TestCase):
    ''' Tests for structures.py '''

    def test_structs(self):
        patlf = PatientLevelFields('patname', 'patid', 'dob', 'sex', 'nstudies')
        stulf = StudyLevelFields('studyid', 'studyuid', 'studydate', 'description', 'nseries')
        serlf = SeriesLevelFields('modality', 'seriesnumber', 'seriesuid',
                                  'description', 'bodypart', 'nimages')
        imglf = ImageLevelFields('imageuid', 'imagenumber')
        combf = ComboFields('patid', 'studyuid', 'studyid', 'studydate',
                            'seriesnumber', 'modality', 'seriesuid',
                            'description', 'nimages', 'firstimageno', 'lastimageno')

        cgetr = CGetResponse('pcid', 'remaining', 'completed', 'failed', 'warning', 'status')
        cstor = CStoreResponse('pcid', 'status')

        self.assertEqual(len(patlf), 5)
        self.assertEqual(len(stulf), 5)
        self.assertEqual(len(serlf), 6)
        self.assertEqual(len(imglf), 2)
        self.assertEqual(len(combf), 11)
        self.assertEqual(len(cgetr), 6)
        self.assertEqual(len(cstor), 2)


if __name__ == '__main__':
    unittest.main()
