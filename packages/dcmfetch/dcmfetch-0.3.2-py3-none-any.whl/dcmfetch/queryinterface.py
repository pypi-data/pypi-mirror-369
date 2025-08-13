#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import attrgetter
from platform import node
from importlib import import_module
import os

from . aettable import AetTable

from . structures import ComboFields, CGetResponse, CStoreResponse, QIError

from . dicomweb import (
    rst_pat_level_find, rst_stu_level_find, rst_ser_level_find,
    rst_img_level_find, rst_ser_level_get, rst_img_level_get
)

toolkit = os.environ.get('DCMTOOLKIT', None)
toolkits = ['dcm4che3', 'pynetdicom', 'mock']
if toolkit:
    toolkits.insert(0, toolkit)

for toolkit in toolkits:
    name = 'qi' + toolkit
    try:
        module = import_module('.' + name, package='dcmfetch')
        (
            dcm_pat_level_find, dcm_stu_level_find, dcm_img_level_get,
            dcm_ser_level_find, dcm_img_level_find, dcm_ser_level_get
        ) = [
            getattr(module, f)
            for f in [
                'dcm_pat_level_find', 'dcm_stu_level_find', 'dcm_img_level_get',
                'dcm_ser_level_find', 'dcm_img_level_find', 'dcm_ser_level_get'
            ]
        ]
        break
    except (ImportError, NotImplementedError) as e:
        print('Import of toolkit %s failed [%s]' % (toolkit, e))
        continue


class QueryInterface:
    def __init__(self, aettable=None, localaet=None):
        """Initialise with the node table and the local (calling) aet to use."""
        if aettable is None:
            aettable = AetTable()
        if localaet is None:
            # NB: max len of aet is 16 chars; the 'Store' suffix is historical
            localaet = node().split('.')[0].replace('-', '')[:11] + 'Store'
        self.aettable = aettable
        self.localaet = localaet


    def pat_level_find(self, servername, patname, patid, birthdate, sex):
        """Patient level find, returns list of PatientLevelFields records."""
        if servername not in self.aettable:
            raise QIError("%s is not in dicom node table" % servername)
        server = self.aettable[servername]

        if 'W' in server.facilities:
            patients = rst_pat_level_find(
                endpoint=server.aet, node=server.host,
                port=server.port, auth=server.auth, scheme=server.scheme,
                patname=patname, patid=patid, birthdate=birthdate, sex=sex
            )
        elif 'F' in server.facilities:
            patients = dcm_pat_level_find(
                aet=server.aet, node=server.host,
                port=server.port, laet=self.localaet,
                patname=patname, patid=patid, birthdate=birthdate, sex=sex
            )
        else:
            raise QIError("%s supports neither dicom query (c-find) operations nor a web rest api" % servername)

        return sorted(patients, key=attrgetter('patname'))


    def combo_find(self, servername, patid, countimages=False):
        """Combination Study and Series Find.

        Returns list of combination study and series onfo records
        One per series.
        Assumed fast enough not to need coroutine/yield interface
        Countimages to be used by dicom layer to query accordngly to get number of images
        """
        if servername not in self.aettable:
            raise QIError("%s is not in dicom node table" % servername)
        server = self.aettable[servername]

        if 'F' not in server.facilities and 'W' not in server.facilities:
            raise QIError("%s supports neither dicom query (c-find) operations nor a web rest api" % servername)

        if 'W' in server.facilities:
            studies = rst_stu_level_find(endpoint=server.aet,
                                         node=server.host,
                                         port=server.port, auth=server.auth, scheme=server.scheme,
                                         patid=patid)
        else:
            studies = dcm_stu_level_find(aet=server.aet,
                                         node=server.host,
                                         port=server.port, laet=self.localaet,
                                         patid=patid)

        comborecords = []
        for study in studies:
            if 'W' in server.facilities:
                serieslist = rst_ser_level_find(
                    endpoint=server.aet,
                    node=server.host, port=server.port, auth=server.auth, scheme=server.scheme,
                    studyuid=study.studyuid
                )
            else:
                serieslist = dcm_ser_level_find(
                    aet=server.aet,
                    node=server.host, port=server.port, laet=self.localaet,
                    patid=patid, studyuid=study.studyuid
                )
            for series in serieslist:
                firstimageno = lastimageno = 0
                nimages = series.nimages
                if countimages:
                    if 'W' in server.facilities:
                        images = rst_img_level_find(
                            endpoint=server.aet,
                            node=server.host, port=server.port, auth=server.auth, scheme=server.scheme,
                            studyuid=study.studyuid, seriesuid=series.seriesuid
                        )
                    else:
                        images = dcm_img_level_find(
                            aet=server.aet,
                            node=server.host, port=server.port, laet=self.localaet,
                            patid=patid, studyuid=study.studyuid, seriesuid=series.seriesuid
                        )
                    imagenos = [image.imagenumber for image in images]
                    firstimageno, lastimageno = min(imagenos), max(imagenos)
                    nimages = len(imagenos)
                else:
                    firstimageno = lastimageno = nimages = None

                if series.description:
                    description = series.description
                elif study.description:
                    description = study.description
                elif series.bodypart:
                    description = series.bodypart
                else:
                    description = 'No Description'

                comborecords.append(
                    ComboFields(
                        patid, study.studyuid, study.studyid, study.studydate,
                        series.seriesnumber, series.modality, series.seriesuid, description,
                        nimages, firstimageno, lastimageno
                    )
                )

        return sorted(comborecords, key=attrgetter('studydate', 'studyid', 'seriesnumber'))


    def image_level_find(self, servername, patid, studyuid, seriesuid):
        """Image level find, returns list of Image records for a series."""
        if servername not in self.aettable:
            raise QIError("%s is not in dicom node table" % servername)

        server = self.aettable[servername]

        if 'W' in server.facilities:
            images = rst_img_level_find(endpoint=server.aet,
                                        node=server.host, port=server.port, auth=server.auth, scheme=server.scheme,
                                        studyuid=studyuid, seriesuid=seriesuid)
        elif 'F' in server.facilities:
            images = dcm_img_level_find(aet=server.aet,
                                        node=server.host, port=server.port, laet=self.localaet,
                                        patid=patid, studyuid=studyuid, seriesuid=seriesuid)
        else:
            raise QIError("%s supports neither dicom query (c-find) operations nor a web rest api" % servername)

        return images


    def series_level_fetch(self, servername, patid, studyuid, seriesuid, savedir):
        """Fetch an image series from the dicom server.

        Implement as C-GET only for now.
        """
        # TODO: see if there is a way of using c-move
        if servername not in self.aettable:
            raise QIError("%s is not in dicom node table" % servername)
        server = self.aettable[servername]

        completed = 0
        remaining = -1

        if 'W' in server.facilities:
            fetch_iter = rst_ser_level_get(
                endpoint=server.aet, node=server.host,
                port=server.port, auth=server.auth, scheme=server.scheme,
                studyuid=studyuid,
                seriesuid=seriesuid, savedir=savedir
            )
        elif 'G' in server.facilities:
            fetch_iter = dcm_ser_level_get(
                aet=server.aet, node=server.host,
                port=server.port, laet=self.localaet,
                patid=patid, studyuid=studyuid,
                seriesuid=seriesuid, savedir=savedir
            )
        else:
            raise QIError("%s supports neither direct (c-get) retrieve operations nor a web rest api" % servername)

        response = None
        for response in fetch_iter:
            if type(response) == CGetResponse:
                completed = response.completed
                remaining = response.remaining
                yield (completed, remaining)
            elif type(response) == CStoreResponse:
                completed += 1
                yield (completed, remaining)

        if response is None:
            return

        if response.status != 0:
            raise QIError("cget final response status non zero (%x)" % response.status)

        return


    def image_level_fetch(self, servername, patid, studyuid, seriesuid, imageuid, savedir):
        """Fetch an image from the dicom server.

        Implement as C-GET only for now.
        """
        # TODO: see if there is a way of using c-move
        if servername not in self.aettable:
            raise QIError("%s is not in dicom node table" % servername)
        server = self.aettable[servername]

        completed = 0
        remaining = -1

        if 'W' in server.facilities:
            fetch_iter = rst_img_level_get(
                endpoint=server.aet, node=server.host,
                port=server.port, auth=server.auth, scheme=server.scheme,
                studyuid=studyuid, seriesuid=seriesuid, imageuid=imageuid,
                savedir=savedir
            )
        elif 'G' in server.facilities:
            fetch_iter = dcm_img_level_get(
                aet=server.aet, node=server.host,
                port=server.port, laet=self.localaet,
                patid=patid, studyuid=studyuid,
                seriesuid=seriesuid, imageuid=imageuid,
                savedir=savedir
            )
        else:
            raise QIError("%s supports neither direct (c-get) retrieve operations nor a web rest api" % servername)

        response = None
        for response in fetch_iter:
            if type(response) == CGetResponse:
                completed = response.completed
                remaining = response.remaining
                yield (completed, remaining)
            elif type(response) == CStoreResponse:
                completed += 1
                yield (completed, remaining)

        if response is None:
            return

        if response.status != 0:
            raise QIError("cget final response status non zero (%x)" % response.status)

        return


if __name__ == '__main__':
    qi = QueryInterface()
    print("Successfully instantiated a QueryInterface()")
    print('Aettable:')
    print(qi.aettable)
    print('Local AET =', qi.localaet)
