#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A dummy DICOM query fetch interface.

This is a dummy plugin for the generic query interface. It is for testing and
allows operation of the web based service even if no dicom tools are installed
"""
from . structures import QIError

#
# TODO: not clear if we are better off raising an error or just returning an empty list
#
def dcm_pat_level_find(aet, node, port, laet, patname, patid, birthdate, sex):
    """Mock patient level query."""
    raise QIError("Query to %s failed, No dicom toolkit available" % aet)


def dcm_stu_level_find(aet, node, port, laet, patid):
    """Mock study level query."""
    raise QIError("Query to %s failed, No dicom toolkit available" % aet)


def dcm_ser_level_find(aet, node, port, laet, patid, studyuid):
    """Mock series level query."""
    raise QIError("Query to %s failed, No dicom toolkit available" % aet)


def dcm_img_level_find(aet, node, port, laet, patid, studyuid, seriesuid):
    """Mock image level query."""
    raise QIError("Query to %s failed, No dicom toolkit available" % aet)


def dcm_ser_level_get(aet, node, port, laet, patid, studyuid, seriesuid, savedir):
    """Mock series level c-get fetch. This is a coroutine."""
    yield None


def dcm_img_level_get(aet, node, port, laet, patid, studyuid, seriesuid, imageuid, savedir):
    """Mock image level c-get fetch."""
    yield None


if __name__ == '__main__':
    print("TODO: Need to write tests for qidmock.py")
