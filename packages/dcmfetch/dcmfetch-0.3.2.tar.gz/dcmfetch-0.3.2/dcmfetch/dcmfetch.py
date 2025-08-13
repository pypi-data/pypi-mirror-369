#!/usr/bin/env python

"""Top level api for dcmfetch package.

Provides high level routines for downloading DICOM series
and a command line program "dcmfetch"
"""

from os.path import join, isdir, normpath, abspath, isfile, exists
from os import mkdir, access, W_OK, X_OK
from shutil import rmtree, move
from tempfile import mkdtemp
from zipfile import ZipFile, is_zipfile, ZIP_STORED
from io import BytesIO
from fnmatch import fnmatchcase

from glob import glob
from itertools import chain
from operator import attrgetter
from datetime import datetime

from pydicom import dcmread

from . queryinterface import QueryInterface
from . aettable import AetTable
from . version import __version__

__all__ = ['fetch_series', 'fetch_series_to_disk', 'read_series']

from collections.abc import Sequence, Callable


def _filter_by_date(dobjs, studydate='all'):
    """Filter on ISO date.

    Used to handle StudyID ambiguity.
    Selects closest study to specified (ISO) date if multiple dates present.

    Parameters
    ----------
    dobjs : sequence of pydicom objects
            input dicom objects
    studydate : str
            'all' or 'earliest'/'first' or 'latest'/'last' or ISO date string

    Returns
    -------
    dobjs : list of pydicom objects
            dicom objects matching date criterion

    """
    if studydate == 'all':
        return list(dobjs)

    if not all('StudyDate' in d for d in dobjs):
        return list(dobjs)

    # Assume Study Dates are ISO date strings so sortable lexographically
    study_dates = sorted(set(d.StudyDate for d in dobjs))
    if len(study_dates) == 1:
        return list(dobjs)

    if studydate in ('earliest', 'first'):
        chosen_date = study_dates[0]
    elif studydate in ('latest', 'last'):
        chosen_date = study_dates[-1]
    else:
        # Closest to specified, NB will raise if not a valid date string
        def days_between(a,  b=studydate):
            return abs((
                datetime.strptime(a, '%Y%m%d') -
                datetime.strptime(b, '%Y%m%d')).days
            )
        chosen_date = min(study_dates, key=days_between)

    return [d for d in dobjs if d.StudyDate == chosen_date]


def fetch_series(patid, stuid='1', sernos=1, server=None, aettable=None,
                 localaet=None, studydate='all', imagesonly=False):
    """Fetch QA series from DICOM store.

    Parameters
    ----------
    patid : str
            Patient ID
    stuid : str
            Study ID (allows glob style matching)
    sernos: int or list of ints (or convertible to int)
            Series number(s) to fetch
    server: str
            Key for server in aet table (default: first defined in nodes file)
    aettable: str
            Dicom nodes file (default: search as defined in QueryInterface)
    localaet: str
            Calling aet (default: construct based on hostname)
    studydate :  str
            'all' or 'earliest'/'first' or 'latest'/'last' or ISO date string
    imagesonly :  bool
            Ignore non-image dicom objects

    Returns
    -------
    dobjs : list of dicom objects
            dicom objects sorted on series and instance number

    """
    qi = QueryInterface(aettable=aettable, localaet=localaet)
    if server is None:
        # first entry in table by default
        server = next(iter(qi.aettable))

    # Fix up for strings and single objects
    if isinstance(sernos, str) or not isinstance(sernos, Sequence):
        sernos = [sernos]
    sernos = list(map(int, sernos))

    # Remove duplicates
    sernos = list(set(sernos))

    seriess = [
        s for s in qi.combo_find(server, patid)
        if fnmatchcase(s.studyid, stuid) and s.seriesnumber in sernos
    ]

    # Retrieve each series in turn to temporary directories
    # series_level_fetch is a generator hence list() to force iteration
    dobjs = []
    for series in seriess:
        tempdir = mkdtemp()
        list(qi.series_level_fetch(
            server,
            patid=patid, studyuid=series.studyuid, seriesuid=series.seriesuid,
            savedir=tempdir
        ))
        dobjs += read_series(tempdir, globspec='*')
        rmtree(tempdir)

    # Restrict by date if not unique.
    # TODO: if many studies may need to filter early w/o holding all in memory
    dobjs = _filter_by_date(dobjs, studydate=studydate)

    # Remove non-image objects.
    # Useful for Philips, which includes PresentationState objects among images
    if imagesonly:
        dobjs = [dobj for dobj in dobjs if 'PixelData' in dobj]

    # Sort by series and instance. Since any retained non-image objects
    # may lack series or image numbers we sort all these to the end of the list.
    return sorted(
        dobjs, key=lambda d: (int(getattr(d, 'SeriesNumber', 1e6)), int(getattr(d, 'InstanceNumber', 1e6)))
    )


def read_series(fileordirname, key=None, numeric=False,
                reverse=False, globspec='*.dcm'):
    """
    Read a DICOM series from a directory or a zip file of DICOM files.

    Optionally sorts the series.

    Parameters
    ----------
    fileordirname:
        List of files, name of dir containing dicom files,
        a zip file or a single dicom file.
    key:
        Sort key - a unary function, a dicom tagname or a list of tag names.
    numeric:
        Sort keys numerically (if a DICOM Tag Name)
    reverse:
        Whether to reverse the direction of sorting
    globspec:
        Glob specification (or list of specs) to match files to read.
        It is ignored in the case of a zip file

    Returns
    -------
    out:
        List of dicom objects.

    """
    if not isinstance(fileordirname, str):
        # Assume a sequence is just a list of simple filenames
        dobjs = [dcmread(fname) for fname in sorted(set(fileordirname))]
    elif isdir(fileordirname):
        # A directory name
        if isinstance(globspec, str):
            # General case is a list of globspecs
            globspec = [globspec]
        # NB: set comprehension takes account of duplicate matches
        # for multiple glob patterns
        files = sorted({
            f for glb in globspec for f in glob(join(fileordirname, glb))
        })
        dobjs = [dcmread(fname) for fname in files]
    elif is_zipfile(fileordirname):
        zf = ZipFile(fileordirname)
        # Unfortunately, the filelike object returned by ZipFile.open()
        # does not provide tell(), which is needed by pydicom.dcmread()
        # so we have to go via a StringIO buffer.
        dobjs = []
        for finfo in zf.infolist():
            sio = BytesIO(zf.read(finfo))
            dobjs.append(dcmread(sio))
            sio.close()
        zf.close()
    elif isfile(fileordirname):
        # Degenerate case - single time point
        dobjs = [dcmread(fileordirname)]
    elif not exists(fileordirname):
        raise IOError(
            "Specified file or directory '%s' does not exist" % fileordirname
        )
    else:
        raise IOError(
            ("'%s' is neither a list of files, " +
             "nor a directory, nor a zip file" +
             "nor yet a plain file") % fileordirname
        )

    if key is not None:
        if isinstance(key, Callable):
            dobjs.sort(key=key, reverse=reverse)
        elif isinstance(key, str):
            if numeric:
                dobjs.sort(
                    key=lambda d: float(getattr(d, key)), reverse=reverse
                )
            else:
                dobjs.sort(key=attrgetter(key), reverse=reverse)
        elif isinstance(key, Sequence) and all(isinstance(x, str) for x in key):
            dobjs.sort(key=attrgetter(*key), reverse=reverse)
        else:
            raise TypeError(
                "Sort key %s should be a string, " +
                "a sequence of strings or a callable" % str(key)
            )

    return dobjs


def fetch_series_to_disk(patid, outdir, studyid='1', sernos=1,
                         server=None, usezip=False):
    """Fetch (multiple) series from DICOM store to disk.

    Parameters
    ----------
    patid : str
            Patient ID
    outdir : str
            Output directory
    studyid : str
            Study ID (allows glob style matching)
    sernos: list of integers
            Series number(s) to fetch
    server: Optional[str]
            DICOM server key in nodes table (default is first entry)
    usezip: Optional[bool]
            package dicom files into zip archive

    Returns
    -------
    int : number of series downloaded

    """
    qi = QueryInterface()
    if server is None:
        # first entry in table by default
        server = next(iter(qi.aettable))

    # Fix up for strings and single objects
    if isinstance(sernos, str) or not isinstance(sernos, Sequence):
        sernos = [sernos]
    sernos = list(map(int, sernos))

    # Remove duplicates
    sernos = list(set(sernos))

    # Filter for the specified study ids and series numbers
    seriess = [
        s for s in qi.combo_find(server, patid)
        if fnmatchcase(s.studyid, studyid) and s.seriesnumber in sernos
    ]

    # Retrieve each series in turn
    count = 0
    for series in seriess:
        # Download initially to temp area
        tempdir = mkdtemp()

        # NB Generator function hence use of list() to force instatiation
        list(qi.series_level_fetch(
            server,
            patid=patid, studyuid=series.studyuid, seriesuid=series.seriesuid,
            savedir=tempdir
        ))

        # filenames constructed from series details - attempts to be unique
        name = (
            '%(modality)s-%(patid)s-%(studydate)s-' +
            '%(studyid)s-%(seriesnumber)03d'
        ) % series._asdict()
        # protect from wildcards in patid
        name = "".join(x for x in name if x.isalnum() or x in '_-')
        imagefiles = glob(join(tempdir, '*'))
        if imagefiles:
            if usezip:
                savefile = normpath(join(outdir, name)) + '.zip'
                zipf = ZipFile(
                    savefile, "w", compression=ZIP_STORED, allowZip64=True
                )
                for n, pathelement in enumerate(imagefiles):
                    archfile = "%s/%05d.dcm" % (name, n + 1)
                    zipf.write(pathelement, archfile)
                zipf.close()
            else:
                savedir = normpath(join(outdir, name))
                if not isdir(savedir):
                    mkdir(savedir)
                for n, pathelement in enumerate(imagefiles):
                    move(pathelement, join(savedir, '%05d.dcm' % (n + 1)))
            count += 1

        rmtree(tempdir)

    return count


def main():

    import argparse
    import sys

    def output_directory(string):
        """Argparse type handler for output directory to write DICOM files to.

        Returns an absolute path.

        """
        path = abspath(string)
        if not isdir(path):
            raise argparse.ArgumentTypeError(
                'the output directory "%s" must exist already' % string
            )
        if not access(path, W_OK | X_OK):
            raise argparse.ArgumentTypeError(
                'the output directory "%s" must be writable' % string
            )
        return path

    def series_numbers(string):
        """Argparse type handler for series numbers.

        Defined by a single integer, an integer range or a comma separated list
        of integers and ranges. Returns a list of integers.
        """
        # Map 'all' to a large range here rather then handle it in fetch_series
        # Range increased to account for large series numbers from Philips.
        # NB: we may need to revisit this.
        MAXSERIESNO = 10000
        if string.lower() == 'all':
            return list(range(1, MAXSERIESNO + 1))

        try:
            seriesnos = []
            numbers_and_ranges = string.split(',')
            for item in numbers_and_ranges:
                range_tokens = item.split('-')
                if len(range_tokens) > 1:
                    # a range
                    start, stop = int(range_tokens[0]), int(range_tokens[-1])
                    seriesnos += list(range(start, stop + 1))
                else:
                    # a number
                    seriesnos += [int(item)]
            seriesnos = list(set(seriesnos))
            if not seriesnos or not all(1 <= n <= MAXSERIESNO for n in seriesnos):
                raise ValueError(
                    'series numbers must be between 1 and %d' % MAXSERIESNO
                )
            return seriesnos
        except ValueError:
            raise argparse.ArgumentTypeError(
                "'%s' is not a valid series number, list or range" % string
            )

    description = 'Fetch DICOM series from Archive Server'
    epilog = (
        'Specify series numbers as a comma separated list of integers' +
        'and ranges without spaces e.g. "-s 1-5,7,8,10-12".'
    )
    try:
        epilog += "\nThe default archive is '%s'" % list(AetTable().keys())[0]
    except (IOError, KeyError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument(
        '-a', '--archive', action='store',
        help='Name of archive server in dicom nodes file'
    )
    parser.add_argument(
        '-p', '--patid', required=True,
        help='Patient to retrieve scans for (an exact string only)'
    )
    parser.add_argument(
        '-S', '--study', default='*',
        help='Study to retrieve scans for (may be a glob pattern)'
    )
    parser.add_argument(
        '-s', '--series', required=True, action='append', type=series_numbers,
        help='Series number, list or range; can specify multiple times'
    )
    parser.add_argument(
        '-z', '--zip', action='store_true',
        help='Pack dicom objects into zip file'
    )
    parser.add_argument(
        '-o', '--out', action='store', default='.', type=output_directory,
        help='Output directory to store series in'
    )
    parser.add_argument(
        '-V', '--version', action='version',
        version='%%(prog)s %s' % __version__
    )

    args = parser.parse_args()

    # flatten list of lists
    sernos = list(chain.from_iterable(args.series))

    nseries = fetch_series_to_disk(
        patid=args.patid,
        outdir=args.out,
        studyid=args.study,
        sernos=sernos,
        server=args.archive,
        usezip=args.zip
    )

    if nseries < 1:
        print(
            'No series found on server matching the specification',
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
