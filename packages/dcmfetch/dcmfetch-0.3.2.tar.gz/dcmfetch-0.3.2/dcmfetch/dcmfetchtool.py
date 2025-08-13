#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A DICOM server browser and fetch tool dialog."""

import sys
from os.path import join, dirname
from os import getenv
from zipfile import ZipFile, ZIP_STORED
from itertools import takewhile

# user interface
from qtpy.QtWidgets import (
    QPushButton, QDialog, QMessageBox,
    QApplication, QGridLayout
)
from qtpy.QtCore import QTimer
from qtpy.compat import getsavefilename

from . fetchdialog import FetchDialog
from . version import __version__


def _common_prefix(strings):
    """Utility: common prefix of a list of strings with trailing '-' cleaned up."""
    def allequal(items):
        return all(item == items[0] for item in items)
    return ''.join(list(zip(*takewhile(allequal, zip(*strings))))[0]).rstrip('-')


class TopLevel(QDialog):

    def __init__(self, aetfile=None, savedir=None, multiple=False, parent=None):
        super(TopLevel, self).__init__(parent)
        self._fetchBtn = QPushButton("Fetch")
        self._saveBtn = QPushButton("Save")
        self._quitBtn = QPushButton("Quit")

        self._fetchBtn.clicked.connect(self.fetch)
        self._saveBtn.clicked.connect(self.save)
        self._quitBtn.clicked.connect(self.reject)

        self._fetchBtn.setEnabled(True)
        self._saveBtn.setEnabled(False)
        self._quitBtn.setEnabled(True)

        grid = QGridLayout()
        grid.addWidget(self._fetchBtn, 0, 0)
        grid.addWidget(self._saveBtn, 0, 1)
        grid.addWidget(self._quitBtn, 0, 2)
        self.setLayout(grid)
        self._fetchDlg = FetchDialog(parent=self, aetfile=aetfile, multiple_selection=multiple)
        self._suggestedFile = ""
        self._fileLists = []
        if savedir is not None:
            self._saveDir = savedir
        else:
            self._saveDir = getenv('USERPROFILE') or getenv('HOME')

    def fetch(self):
        self._fetchDlg.exec_()
        if self._fetchDlg.result() == QDialog.Accepted:
            self._suggestedFiles = self._fetchDlg.series_filenames
            if self._fetchDlg.multiple_selection:
                self._fileLists = self._fetchDlg.get_image_files()
            else:
                self._fileLists = [self._fetchDlg.get_image_files()]
            self._saveBtn.setEnabled(True)
        else:
            self._saveBtn.setEnabled(False)

    def save(self):
        if self._suggestedFiles and self._fileLists:
            try:
                suggested_zip_name = join(self._saveDir, _common_prefix(self._suggestedFiles))
                zip_name, _ = getsavefilename(self, "Save Zip File", suggested_zip_name, '*.zip')
                if not zip_name:
                    return

                with ZipFile(zip_name, "w", compression=ZIP_STORED, allowZip64=True) as zipf:
                    for filelist, series_name in zip(self._fileLists, self._suggestedFiles):
                        for (n, pathelement) in enumerate(filelist, start=1):
                            archfile = join(series_name, "%05d.dcm" % n)
                            zipf.write(pathelement, archfile)
            except IOError as e:
                print('Save File: IOError! (%s)' % e, file=sys.stderr)
                return

            self._saveBtn.setEnabled(False)
            self._fetchDlg.free_image_files()
            self._suggestedFiles = []
            self._fileLists = []
            self._saveDir = dirname(zip_name)

    def checkSave(self):
        if self._fileLists:
            msgBox = QMessageBox()
            msgBox.setText("The series has not been saved.")
            msgBox.setInformativeText("Do you want to save it now?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)

            while self._fileLists:
                ret = msgBox.exec_()
                if ret == QMessageBox.Save:
                    self.save()
                elif ret == QMessageBox.Discard:
                    self._fetchDlg.free_image_files()
                    self._suggestedFile = ""
                    self._fileLists = []
                    return True
                else:
                    return False
        return True

    def reject(self):
        if self.checkSave():
            self.close()

    def closeEvent(self, event):
        if self.checkSave():
            super(TopLevel, self).closeEvent(event)
            event.accept()
        else:
            event.ignore()


def main():
    from argparse import ArgumentParser, ArgumentTypeError
    from signal import signal, SIGINT
    from os.path import isdir, normpath, abspath
    from os import access, W_OK, X_OK

    def output_directory(string):
        """Argparse type handler for an output directory to write DICOM files to.

        Returns an absolute path.
        """
        path = normpath(abspath(string))
        if not isdir(path):
            raise ArgumentTypeError('the output directory "%s" must exist already' % string)
        if not access(path, W_OK | X_OK):
            raise ArgumentTypeError('the output directory "%s" must be writable' % string)
        return path

    parser = ArgumentParser(
        description='Fetch DICOM series from Archive Server'
    )
    parser.add_argument(
        '-V', '--version',
        action='version', version='%%(prog)s %s' % __version__
    )
    parser.add_argument(
        '-o', '--out', action='store',
        type=output_directory, help='Output directory to store series in'
    )
    parser.add_argument(
        '-m', '--multiple', action='store_true',
        help='Fetch multiple series'
    )

    args = parser.parse_args()

    try:
        app = QApplication(sys.argv)

        # Boiler-plate code to handle Ctrl-C cleanly
        t = QTimer(); t.start(500); t.timeout.connect(lambda: None)
        signal(SIGINT, lambda sig, frame: QApplication.quit())

        toplevel = TopLevel(savedir=args.out, multiple=args.multiple)
        toplevel.show()
        app.exec_()
    except Exception as e:
        print('Top level exception: %s' % e, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
