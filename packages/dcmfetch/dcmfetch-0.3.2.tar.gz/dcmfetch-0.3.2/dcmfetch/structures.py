#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Structures for DICOM requests and responses
"""
from collections import namedtuple

__all__ = [
    'PatientLevelFields', 'StudyLevelFields', 'SeriesLevelFields',
    'ImageLevelFields', 'ComboFields',
    'CGetResponse', 'CStoreResponse',
    'QIError'
]

PatientLevelFields = namedtuple(
    'PatientLevelFields',
    'patname, patid, dob, sex, nstudies'
)
StudyLevelFields = namedtuple(
    'StudyLevelFields',
    'studyid, studyuid, studydate, description, nseries'
)
SeriesLevelFields = namedtuple(
    'SeriesLevelFields',
    'modality, seriesnumber, seriesuid, description, bodypart, nimages'
)
ImageLevelFields = namedtuple(
    'ImageLevelFields',
    'imageuid, imagenumber'
)
ComboFields = namedtuple(
    'ComboFields',
    ', '.join([
        'patid', 'studyuid', 'studyid', 'studydate',
        'seriesnumber', 'modality', 'seriesuid',
        'description', 'nimages', 'firstimageno', 'lastimageno'
    ])
)

CGetResponse = namedtuple(
    'CGetResponse',
    'pcid, remaining, completed, failed, warning, status'
)
CStoreResponse = namedtuple(
    'CStoreResponse',
    'pcid, status'
)


class QIError(Exception):
    """Exception Class."""

    pass


if __name__ == '__main__':
    PatientLevelFields()
    StudyLevelFields()
    SeriesLevelFields()
    ImageLevelFields()
    ComboFields()
    CGetResponse()
    CStoreResponse()
    try:
        raise QIError('An Error')
    except QIError as e:
        assert str(e) == 'An Error'
