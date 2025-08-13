#!/usr/bin/env python
"""
Implements an interface to the DICOM WEB restful api.

The restful interface itself supports three services which correspond
to the native DICOM services:
 - qido-rs (c-find)
 - wado-rs (c-get)
 - stow-rs (c-store).

These are presented here in an api that matches the query interface one
in queryinterface.py so it can be used as a drop in alternative where
the dicom server (eg Orthanc) supports this protocol.
"""

import sys
from os.path import join
import email
from hashlib import md5
import requests

from . structures import (
    PatientLevelFields, StudyLevelFields,
    SeriesLevelFields, ImageLevelFields,
    CStoreResponse
)

__all__ = [
    'rst_pat_level_find', 'rst_stu_level_find', 'rst_ser_level_find',
    'rst_img_level_find', 'rst_ser_level_get', 'rst_img_level_get'
]


def _get_simple_tag(json, tagname, default=None):
    """
    Get field from dicom json response, handling missing and empty values

    Parameters
    ----------
    json: json struct
        json response from server
    tagname: str
        name of tagname to extract
    default:
        value to return if field is missing or empty

    Returns
    -------
        value of field
    """
    # Tag not present at all
    if tagname not in json:
        return default
    else:
        field = json[tagname]
    # Tag is present but empty (as per dicom standard the 'Value' entry will be missing)
    if 'Value' not in field:
        return default
    else:
        value = field['Value']
    # Value should be a list - if it is empty then just use the default
    return value[0] if value else default
 

def _get_pn_tag(json, tagname, default):
    """
    Get a patient name field from dicom json response, handling missing and empty values

    Parameters
    ----------
    json: json struct
        json response from server
    tagname: str
        name of tagname to extract
    default:
        value to return if field is missing or empty

    Returns
    -------
        value of field
    """
    return _get_simple_tag(json, tagname, {}).get('Alphabetic', default)



def rst_pat_level_find(endpoint, node, port, auth, scheme, patname, patid, birthdate, sex):
    """
    Patient level find using DICOM QIDO-RS rest API.

    Behaves similarly to a DICOM Patient Level C-FIND
    but uses StudyRoot hierarchy of QI-RS API.

    Parameters
    ----------
    endpoint : str
        Root of QI-RS/WADO-RS in URL.
    node : str
        Hostname.
    port: int
        TCP port number
    auth: str or None
        Colon separated username:password combination
    scheme: str
        URI scheme (http or https)
    patname: str
        Patient Name search string including wildcards
    patid: str
        Patient Identifier search string including wildcards
    birthdate: str
        Patient Birthdate search string including wildcards
    sex: str
        Patient Sex M|F|O or wild card

    Returns
    -------
    list
        Sorted list of matching PatientLevelFields structures

    """
    PATNAME = "00100010"
    PATID = "00100020"
    PATBDATE = "00100030"
    PATSEX = "00100040"

    # dates can be '' for all or an a-b range but not '*'
    if '*' in birthdate:
        birthdate = ''

    query = {
        'PatientName': patname,
        'PatientID': patid,
        'PatientBirthDate': birthdate,
        'PatientSex': sex
    }
    accept = {'Accept': 'application/json'}
    url = '%s://%s:%d/%s/studies/' % (scheme, node, port, endpoint)
    with requests.Session() as s:
        if auth is not None:
            user, passwd = auth.split(':')
            http_response = s.get(url, auth=(user, passwd), headers=accept, params=query)
        else:
            http_response = s.get(url, headers=accept, params=query)

    http_response.raise_for_status()

    matches = http_response.json()
    patients = [
        PatientLevelFields(
            str(_get_pn_tag(match, PATNAME, 'NoName')),
            str(_get_simple_tag(match, PATID, 'NoID')),
            str(_get_simple_tag(match, PATBDATE, 'NoDOB')),
            str(_get_simple_tag(match, PATSEX, 'O')),
            0
        ) for match in matches
    ]

    return sorted(set(patients))


def rst_stu_level_find(endpoint, node, port, auth, scheme, patid):
    """
    Study level find using DICOM QIDO-RS rest API.

    Behaves similarly to a DICOM Study Level C-FIND
    but uses QIDO-RS API. Assume that Patients are uniquely identified by ID.

    Parameters
    ----------
    endpoint : str
        Root of QIDO-RS/WADO-RS in URL.
    node : str
        Hostname.
    port: int
        TCP port number
    auth: str or None
        Colon separated username:password combination
    scheme: str
        URI scheme (http or https)
    patid: str
        Explicit unique PatientID (no wild cards)

    Returns
    -------
    list
        Sorted list of matching StudyLevelFields structures for the specified Patient

    """
    STUDYID = "00200010"
    STUDYUID = "0020000D"
    STUDYDATE = "00080020"
    STUDYDESCR = "00081030"

    query = {'PatientID': patid}
    accept = {'Accept': 'application/json'}
    url = '%s://%s:%d/%s/studies/' % (scheme, node, port, endpoint)

    with requests.Session() as s:
        if auth is not None:
            user, passwd = auth.split(':')
            http_response = s.get(url, auth=(user, passwd), headers=accept, params=query)
        else:
            http_response = s.get(url, headers=accept, params=query)

    http_response.raise_for_status()

    matches = http_response.json()

    studies = []
    nseries = 0
    for match in matches:
        if STUDYUID in match:
            studyuid = str(match[STUDYUID]['Value'][0])
        else:
            raise ValueError('No Study UID in match')
        studyid = str(_get_simple_tag(match, STUDYID, 'NoStudyID'))
        studydate = str(_get_simple_tag(match, STUDYDATE, 'NoStudyDate'))
        studydescr = str(_get_simple_tag(match, STUDYDESCR, 'NoStudyDescr'))
        studies.append(StudyLevelFields(studyid, studyuid, studydate, studydescr, nseries))

    return studies


def rst_ser_level_find(endpoint, node, port, auth, scheme, studyuid):
    """
    Series level find using DICOM QIDO-RS rest API.

    Behaves similarly to a DICOM Series Level C-FIND but uses QIDO-RS API.
    The patient id is not required as the rest api is study rooted.

    Parameters
    ----------
    endpoint : str
        Root of QIDO-RS/WADO-RS in URL.
    node : str
        Hostname.
    port: int
        TCP port number
    auth: str or None
        Colon separated username:password combination
    scheme: str
        URI scheme (http or https)
    studyuid: str
        DICOM Study UID

    Returns
    -------
    list
        Sorted list of matching SeriesLevelFields structures for the specified Study

    """
    SERIESMODALITY = "00080060"
    SERIESNUMBER = "00200011"
    SERIESUID = "0020000E"
    SERIESDESCR = "0008103E"
    SERIESBODYPART = "00180015"

    query = {'Modality': ''}
    accept = {'Accept': 'application/json'}
    url = '%s://%s:%d/%s/studies/%s/series' % (scheme, node, port, endpoint, studyuid)

    with requests.Session() as s:
        if auth is not None:
            user, passwd = auth.split(':')
            http_response = s.get(url, auth=(user, passwd), headers=accept, params=query)
        else:
            http_response = s.get(url, headers=accept, params=query)

    http_response.raise_for_status()

    matches = http_response.json()

    series = []
    nimages = 0
    for match in matches:
        if SERIESUID in match:
            seriesuid = str(match[SERIESUID]['Value'][0])
        else:
            raise ValueError('No Series UID in match')
        modality = str(_get_simple_tag(match, SERIESMODALITY, 'NoModality'))
        number = int(_get_simple_tag(match, SERIESNUMBER, -1))
        description = str(_get_simple_tag(match, SERIESDESCR, 'NoSeriesDescr'))
        bodypart = str(_get_simple_tag(match, SERIESBODYPART, 'NoSeriesBodyPart'))
        series.append(SeriesLevelFields(modality, number, seriesuid, description, bodypart, nimages))
    return series


def rst_img_level_find(endpoint, node, port, auth, scheme, studyuid, seriesuid):
    """Image level find using DICOM QIDO-RS rest API.

    Behaves similarly to a DICOM Image Level C-FIND but uses QIDO-RS API.
    The patient id is not required as the rest api is study rooted.

    Parameters
    ----------
    endpoint : str
        Root of QIDO-RS/WADO-RS in URL.
    node : str
        Hostname.
    port: int
        TCP port number
    auth: str or None
        Colon separated username:password combination
    scheme: str
        URI scheme (http or https)
    studyuid: str
        DICOM Study UID
    seriesuid: str
        DICOM Series UID

    Returns
    -------
    list
        Sorted list of matching SeriesLevelFields structures for the specified Study

    """
    INSTANCENUMBER = "00200013"
    INSTANCEUID = "00080018"

    query = {'InstanceNumber': ''}
    accept = {'Accept': 'application/json'}
    url = '%s://%s:%d/%s/studies/%s/series/%s/instances' % (scheme, node, port, endpoint, studyuid, seriesuid)

    with requests.Session() as s:
        if auth is not None:
            user, passwd = auth.split(':')
            http_response = s.get(url, auth=(user, passwd), headers=accept, params=query)
        else:
            http_response = s.get(url, headers=accept, params=query)

    http_response.raise_for_status()

    matches = http_response.json()

    images = []
    for match in matches:
        if INSTANCEUID in match:
            instanceuid = str(match[INSTANCEUID]['Value'][0])
        else:
            raise ValueError('No Instance UID in match')
        number = int(_get_simple_tag(match, INSTANCENUMBER, -1))
        images.append(ImageLevelFields(instanceuid, number))

    return images


def rst_ser_level_get(endpoint, node, port, auth, scheme, studyuid, seriesuid, savedir):
    """Series level get using DICOM WADO-RS rest API.

    Behaves similarly to a DICOM Series Level C-GET but uses WADO-RS API.
    The patient id is not required as the rest api is study rooted.
    The function is a generator and yields for each dicom object extracted
    from the returned multipart and saved to the given directory as a part 10 file.

    Parameters
    ----------
    endpoint : str
        Root of QIDO-RS/WADO-RS in URL.
    node : str
        Hostname.
    port: int
        TCP port number
    auth: str or None
        Colon separated username:password combination
    scheme: str
        URI scheme (http or https)
    studyuid: str
        DICOM Study UID
    seriesuid: str
        DICOM Series UID
    savedir: str
        Existing directory to save DICOM objects to.

    Returns
    -------
    Function is a generator

    """
    url = '%s://%s:%d/%s/studies/%s/series/%s' % (scheme, node, port, endpoint, studyuid, seriesuid)

    with requests.Session() as s:
        if auth is not None:
            user, passwd = auth.split(':')
            http_response = s.get(url, auth=(user, passwd))
        else:
            http_response = s.get(url)

    http_response.raise_for_status()

    #  Construct valid mime by prepending content type
    hdr = ('Content-Type: ' + http_response.headers['Content-Type']).encode()
    msg = email.message_from_bytes(hdr + b'\r\n' + http_response.content)
    serieshash = md5(seriesuid.encode()).digest().hex().upper()

    fileno = 1
    for part in msg.walk():
        dcmdata = part.get_payload(decode=True)
        if dcmdata is not None:
            filename = join(savedir, 'S%sI%04d.dcm' % (serieshash, fileno))
            with open(filename, 'wb') as f:
                f.write(dcmdata)
            fileno += 1
            #  dummy
            yield CStoreResponse(0, 0)
    return


def rst_img_level_get(endpoint, node, port, auth, scheme, studyuid, seriesuid, imageuid, savedir):
    """Image level get using DICOM WADO-RS rest API.

    Behaves similarly to a DICOM Image Level C-GET but uses WADO-RS API.
    The patient id is not required as the rest api is study rooted.
    The function is a generator and yields for each dicom object extracted
    from the returned multipart and saved to the given directory as a part 10 file
    for consistency with the series level get. However we expect a single object only.

    Parameters
    ----------
    endpoint : str
        Root of QIDO-RS/WADO-RS in URL.
    node : str
        Hostname.
    port: int
        TCP port number
    auth: str or None
        Colon separated username:password combination
    scheme: str
        URI scheme (http or https)
    studyuid: str
        DICOM Study UID
    seriesuid: str
        DICOM Series UID
    imageuid: str
        DICOM SOP Instance (ie Image) UID
    savedir: str
        Existing directory to save DICOM objects to.

    Returns
    -------
    Function is a generator

    """
    url = (
        '%s://%s:%d/%s/studies/%s/series/%s/instances/%s' %
        (scheme, node, port, endpoint, studyuid, seriesuid, imageuid)
    )

    with requests.Session() as s:
        if auth is not None:
            user, passwd = auth.split(':')
            http_response = s.get(url, auth=(user, passwd))
        else:
            http_response = s.get(url)

    http_response.raise_for_status()

    # Construct valid mime by prepending content type
    hdr = ('Content-Type: ' + http_response.headers['Content-Type']).encode()
    msg = email.message_from_bytes(hdr + b'\r\n' + http_response.content)

    fileno = 1
    for part in msg.walk():
        dcmdata = part.get_payload(decode=True)
        if dcmdata is not None:
            filename = join(savedir, '%04d.dcm' % fileno)
            with open(filename, 'wb') as f:
                f.write(dcmdata)
            fileno += 1
            # dummy
            # TODO decide on form of response CGetResponse may be more logical
            # make a new one for WadoRsResponse
            yield CStoreResponse(0, 0)
    return


if __name__ == '__main__':
    print("Module dicomweb.py - see tests/ dir for unit tests")
