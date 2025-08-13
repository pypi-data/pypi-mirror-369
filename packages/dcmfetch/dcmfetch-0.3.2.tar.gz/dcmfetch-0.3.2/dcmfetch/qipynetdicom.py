#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DICOM query fetch interface based on pynetdicom at  https://github.com/pydicom/pynetdicom.
"""

import os
from threading import Thread
from os.path import join
from queue import Queue, Empty

from pydicom.dataset import Dataset
from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian

from pynetdicom import (
    AE, build_role, evt,
    StoragePresentationContexts,
    QueryRetrievePresentationContexts
)

# typos etc in old versions of pynetdicom
try:
    from pynetdicom.sop_class import Verification
except ImportError:
    from pynetdicom.sop_class import VerificationSOPClass as Verification
try:
    from pynetdicom.sop_class import PerformedImagingAgentAdministrationSRStorage
except ImportError:
    from pynetdicom.sop_class import PerformedImagingAgestAdministrationSRStorage as PerformedImagingAgentAdministrationSRStorage

from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelGet,
    PlannedImagingAgentAdministrationSRStorage,
    EncapsulatedSTLStorage
)

from . structures import (
    PatientLevelFields, StudyLevelFields, SeriesLevelFields,
    ImageLevelFields,
    CGetResponse, CStoreResponse,
    QIError
)


def _get_tag(dobj, name, default):
    """
    Get attribute from DICOM object with None handling

    """
    tagval = getattr(dobj, name, default)
    return tagval if tagval is not None else default


def dcm_pat_level_find(aet, node, port, laet, patname, patid, birthdate, sex):
    """
    Use pynetdicom to perform a patient level query.

    The result is a list of PatientLevelFields records.

    """
    ae = AE(laet)
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

    # Query dataset
    ds = Dataset()
    ds.QueryRetrieveLevel = 'PATIENT'

    ds.PatientName = patname
    ds.PatientID = patid
    ds.PatientBirthDate = birthdate
    ds.PatientSex = sex
    ds.NumberOfPatientRelatedStudies = ''

    assoc = ae.associate(node, port, ae_title=aet)
    responses = []
    if assoc.is_established:
        matches = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
        for state, d in matches:
            if state and state.Status in (0xFF00, 0xFF01):
                responses.append(
                    PatientLevelFields(
                        patname  = str(_get_tag(d, 'PatientName', 'Unknown')),
                        patid    = _get_tag(d, 'PatientID', ''),
                        dob      = str(_get_tag(d, 'PatientBirthDate', '')),
                        sex      = _get_tag(d, 'PatientSex', ''),
                        nstudies = int(_get_tag(d, 'NumberOfPatientRelatedStudies', 0))
                    )
                )
        assoc.release()
    else:
        raise QIError('Unable to establish association)')

    return responses


def dcm_stu_level_find(aet, node, port, laet, patid):
    """Use pynetdicom to perform a study level query.

    The result is a list of StudyLevelFields records.

    """
    ae = AE(laet)
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

    # Query dataset
    ds = Dataset()
    ds.QueryRetrieveLevel = 'STUDY'
    ds.PatientID = patid

    ds.StudyInstanceUID = ''
    ds.StudyID = ''
    ds.StudyDate = ''
    ds.StudyDescription = ''
    ds.NumberOfStudyRelatedSeries = ''

    assoc = ae.associate(node, port, ae_title=aet)
    responses = []
    if assoc.is_established:
        matches = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
        for state, d in matches:
            if state and state.Status in (0xFF00, 0xFF01):
                responses.append(
                    StudyLevelFields(
                        studyid     = _get_tag(d, 'StudyID', ''),
                        studyuid    = _get_tag(d, 'StudyInstanceUID', ''),
                        studydate   = _get_tag(d, 'StudyDate', ''),
                        description = _get_tag(d, 'StudyDescription', ''),
                        nseries     = int(_get_tag(d, 'NumberOfStudyRelatedSeries', 0))
                    )
                )
        assoc.release()
    else:
        raise QIError('Unable to establish association)')

    return responses


def dcm_ser_level_find(aet, node, port, laet, patid, studyuid):
    """
    Use pynetdicom to perform a series level query.

    The result is a list of SeriesLevelFields records.
    """
    ae = AE(laet)
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

    # Query dataset
    ds = Dataset()
    ds.QueryRetrieveLevel = 'SERIES'
    ds.PatientID = patid
    ds.StudyInstanceUID = studyuid

    ds.Modality = ''
    ds.SeriesNumber = ''
    ds.SeriesInstanceUID = ''
    ds.SeriesDescription = ''
    ds.BodyPartExamined = ''
    ds.NumberOfSeriesRelatedInstances = ''

    assoc = ae.associate(node, port, ae_title=aet)
    responses = []
    if assoc.is_established:
        matches = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
        for state, d in matches:
            if state and state.Status in (0xFF00, 0xFF01):
                responses.append(
                    SeriesLevelFields(
                        modality     = _get_tag(d, 'Modality', ''),
                        seriesnumber = int(_get_tag(d, 'SeriesNumber', 0)),
                        seriesuid    = _get_tag(d, 'SeriesInstanceUID',  ''),
                        description  = _get_tag(d, 'SeriesDescription', ''),
                        bodypart     = _get_tag(d, 'BodyPartExamined', ''),
                        nimages      = int(_get_tag(d, 'NumberOfSeriesRelatedInstances', 0))
                    )
                )
        assoc.release()
    else:
        raise QIError('Unable to establish association)')

    return responses


def dcm_img_level_find(aet, node, port, laet, patid, studyuid, seriesuid):
    """Use pynetdicom to perform a image level query.

    The result is a list of ImageLevelFields records.
    """
    ae = AE(laet)
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

    # Query dataset
    ds = Dataset()
    ds.QueryRetrieveLevel = 'IMAGE'
    ds.PatientID = patid
    ds.StudyInstanceUID = studyuid
    ds.SeriesInstanceUID = seriesuid

    ds.SOPInstanceUID = ''
    ds.InstanceNumber = ''

    assoc = ae.associate(node, port, ae_title=aet)
    responses = []
    if assoc.is_established:
        matches = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
        for state, d in matches:
            if state and state.Status in (0xFF00, 0xFF01):
                responses.append(
                    ImageLevelFields(
                        imageuid    = _get_tag(d, 'SOPInstanceUID', ''),
                        imagenumber = int(_get_tag(d, 'InstanceNumber', 0))
                    )
                )
        assoc.release()
    else:
        raise QIError('Unable to establish association')

    return responses



def dcm_ser_level_get(aet, node, port, laet, patid, studyuid, seriesuid, savedir):
    """
    Use pynetdicom to perform a series level c-get fetch.

    This is a coroutine/generator.

    Each response yields a CGetResponse record to the caller. The yield is tied to the
    c-store messages rather than (as would be more natural) the c-get responses because
    dcm4chee (at least) doesn't seem to issue the intermediate pending c-get responses.

    The retrieved objects are left as files in the given save directory.

    Ths routine just yields items from a queue that is filled by _pynetdicom_ser_get_worker
    """
    queue = Queue()

    dcmthread = Thread(
        target=_pynetdicom_ser_get_worker,
        args=[aet, node, port, laet, patid, studyuid, seriesuid, savedir, queue],
        kwargs={}
    )
    dcmthread.daemon = True

    dcmthread.start()
    while dcmthread.is_alive():
        try:
            item = queue.get(block=True, timeout=1)
            yield item
            queue.task_done()
        except Empty:
            pass
    return


def _pynetdicom_ser_get_worker(aet, node, port, laet, patid, studyuid, seriesuid, savedir, queue):
    """
    Use pynetdicom to perform a series level c-get fetch.

    This is to be run in a separate worker thread. The c-store callbacks save
    the images and push a CStoreResponse object onto a queue for the main thread.
    The function returns normally, which will lead to the threading terminating.
    This is detected by the parent thread.

    The retrieved objects are left as files in the given save directory.

    Some relevant error codes:
        Success = 0x0000
        Pending = 0xff00
        Warning = 0xb000
        Cancelled = 0xfe00
        UnableToMatch = 0xa701
        UnableToSubOps = 0xa702
        SOPClassMisMatch = 0xa900
    """

    # If we conly get the c-store events rathewr than the pending respinses we need to know how many objects are expected
    nmatches = len(dcm_img_level_find(aet, node, port, laet, patid, studyuid, seriesuid))

    def _store_event_handler(event, counters):
        counters[0] += 1
        counter = counters[0]
        try:
            ds = event.dataset
            # Remove any Group 0x0002 elements that may have been included
            ds = ds[0x00030000:]
        except IndexError:
            # Unable to decode dataset
            status = 0x0117
            queue.put(CStoreResponse(counter, status))
            return status


        # Add the file meta information elements
        ds.file_meta = event.file_meta

        # As pydicom uses deferred reads, decoding errors
        # are hidden until triggered by accessing a faulty element
        try:
            sop_instance = ds.SOPInstanceUID
        except AttributeError:
            # Unable to decode dataset
            status = 0x0120
            queue.put(CStoreResponse(counter, status))
            return status

        try:
            # Using enforce_file_format=True ensures a compliant
            # File Meta Information Header is written
            filename = join(savedir, "%s" % sop_instance)
            ds.save_as(filename, enforce_file_format=True)
        except IOError:
            # Out of Resources
            status = 0xA700
            queue.put(CStoreResponse(counter, status))
            return status

        status = 0x0000
        queue.put(CStoreResponse(counter, status))
        return status


    # Create application entity
    ae = AE(ae_title=laet)
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)

    query = Dataset()
    query.QueryRetrieveLevel = 'SERIES'
    query.PatientID = patid
    query.StudyInstanceUID = studyuid
    query.SeriesInstanceUID = seriesuid    

    # Add all storage SOP classes except these
    _excluded_contexts = [
        PlannedImagingAgentAdministrationSRStorage,
        PerformedImagingAgentAdministrationSRStorage,
        EncapsulatedSTLStorage,
    ]
    store_contexts = [
        cx for cx in StoragePresentationContexts
        if cx.abstract_syntax not in _excluded_contexts
    ]
    for cx in store_contexts:
        # Prefer Explicit VR for c-store; also works around issue with dcm4che3 dcmqrscp
        # where it seems to accept Implicit but tries to use Explicit in c-store
        ae.add_requested_context(cx.abstract_syntax, [ExplicitVRLittleEndian, ImplicitVRLittleEndian])

    # Add SCP/SCU Role Selection to the extended negotiation (we want to act as a Storage SCP)
    roles = [build_role(cx.abstract_syntax, scp_role=True) for cx in store_contexts]

    # (Mutable) counter for responses
    counters = [1]

    # Request association
    assoc = ae.associate(
        node,
        port,
        ae_title=aet,
        ext_neg=roles,
        evt_handlers=[(evt.EVT_C_STORE, _store_event_handler, (counters,))]
    )
    if assoc.is_established:
        # Send query
        responses = assoc.send_c_get(query, PatientRootQueryRetrieveInformationModelGet)
        queue.put(CGetResponse(0, nmatches, 0, 0, 0, 0))
        for state, identifier in responses:
            if state:
                status = state.Status
                if status in (0xFF00, 0xFF01):
                    # pending: continuing
                    ncompleted = state.NumberOfCompletedSuboperations
                    nfailed = state.NumberOfFailedSuboperations
                    nwarnings = state.NumberOfWarningSuboperations
                    nremaining = nmatches - (ncompleted + nfailed + nwarnings)
                else:
                    # final
                    ncompleted = state.NumberOfCompletedSuboperations
                    nfailed = state.NumberOfFailedSuboperations
                    nwarnings = state.NumberOfWarningSuboperations
                    nremaining = nmatches - (ncompleted + nfailed + nwarnings)
                queue.put(CGetResponse(counters[0], nremaining, ncompleted, nfailed, nwarnings, status))
        assoc.release()
    else:
        raise QIError('Association from %s to %s:%3d/%s rejected' % (laet, node, port, aet))


def dcm_img_level_get(aet, node, port, laet, patid, studyuid, seriesuid, imageuid, savedir):
    """
    Use pynetdicom to perform an image level c-get fetch.

    This is a coroutine/generator but will yield just a single CGetResponse record to the caller.

    The retrieved object is left as a file in the given save directory.
    """

   # The callback function for C-STORE sub-operations
    def _store_event_handler(event):
        try:
            ds = event.dataset
            # Remove any Group 0x0002 elements that may have been included
            ds = ds[0x00030000:]
        except IndexError:
            # Unable to decode dataset
            status = 0x0117
            return 0x0117

        # Add the file meta information elements
        ds.file_meta = event.file_meta

        # As pydicom uses deferred reads, decoding errors
        # are hidden until triggered by accessing a faulty element
        try:
            sop_instance = ds.SOPInstanceUID
        except AttributeError:
            # Unable to decode dataset
            return 0x0120

        try:
            # Using enforce_file_format=True ensures a compliant
            # File Meta Information Header is written
            filename = join(savedir, "%s" % sop_instance)
            ds.save_as(filename, enforce_file_format=True)
        except IOError:
            # Out of Resources
            return 0xA700

        return 0x0000

    # Create application entity
    ae = AE(ae_title=laet)
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)

    query = Dataset()
    query.QueryRetrieveLevel = 'IMAGE'
    query.PatientID = patid
    query.StudyInstanceUID = studyuid
    query.SeriesInstanceUID = seriesuid    
    query.SOPInstanceUID = imageuid    

    # Add all storage SOP classes except these
    _excluded_contexts = [
        PlannedImagingAgentAdministrationSRStorage,
        PerformedImagingAgentAdministrationSRStorage,
        EncapsulatedSTLStorage,
    ]
    store_contexts = [
        cx for cx in StoragePresentationContexts
        if cx.abstract_syntax not in _excluded_contexts
    ]
    for cx in store_contexts:
        # Prefer Explicit VR for c-store; also works around issue with dcm4che3 dcmqrscp
        # where it seems to accept Implicit but tries to use Explicit in c-store
        ae.add_requested_context(cx.abstract_syntax, [ExplicitVRLittleEndian, ImplicitVRLittleEndian])

    # Add SCP/SCU Role Selection to the extended negotiation (we want to act as a Storage SCP)        
    roles = [build_role(cx.abstract_syntax, scp_role=True) for cx in store_contexts]

    # Request association
    assoc = ae.associate(
        node,
        port,
        ae_title=aet,
        ext_neg=roles,
        evt_handlers=[(evt.EVT_C_STORE, _store_event_handler)]
    )
    if assoc.is_established:
        # Send query
        responses = assoc.send_c_get(query, PatientRootQueryRetrieveInformationModelGet)
        for index, (status, identifier) in enumerate(responses, 1):
            ncompleted = status.NumberOfCompletedSuboperations
            nfailed = status.NumberOfFailedSuboperations
            nwarnings = status.NumberOfWarningSuboperations
            nremaining = 1 - (ncompleted + nfailed + nwarnings)
            yield CGetResponse(index, nremaining, ncompleted, nfailed, nwarnings, status.Status)
        assoc.release()
    else:
        raise QIError('Association from %s to %s:%3d/%s rejected' % (laet, node, port, aet))


if __name__ == '__main__':
    print("Tests for qipynetdicom.py are in dcmfetch/tests")
