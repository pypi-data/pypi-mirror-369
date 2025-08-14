#!/usr/bin/env python
# encoding: utf-8
"""
anaio.py

A C extension for Python to read ana f0 files. Based on Michiel van Noort's
IDL DLM library 'f0' which contains a cleaned up version of the original
anarw routines.

To read a file:
> anadata = anaio.fzread(<filename>, [debug=0])
which will return a dict with the data in anadata['data'] and some meta info in anadata['header'].
To return only the data or header, use anaio.getdata() and anaio.getheader() respectively.
The letter will also not read the data and therefore speed up the process if you are interested in the header only.

To write a file:
> anaio.fzwrite(<filename>, <data>, [compress=1, [comments=False, [debug=0]]]):
or use anaio.writeto(), which is an alias to fzwrite().

Created by Tim van Werkhoven (t.i.m.vanwerkhoven@gmail.com) on 2009-02-11.
Copyright (c) 2009--2011 Tim van Werkhoven.
Since 2020 maintained and extended by Johannes Hoelken (hoelken@mps.mpg.de).

Published under MIT license.
"""

import os
import unittest

from ._anaio import fzread as _fzread, fzwrite as _fzwrite, fzhead as _fzhead


def fzread(filename, debug=0):
    """
    Load an ANA file and return the data, size, dimensions and comments in a
    dict.

    data = pyana.load(filename)
    """
    if not os.path.isfile(filename):
        raise IOError("File does not exist!")

    return _fzread(filename, debug)


def fzhead(filename: str) -> str:
    """
    Load only the header (comment) of an ANA file.

    header = pyana.getheader(filename)
    """
    if not os.path.isfile(filename):
        raise IOError("File does not exist!")

    return _fzhead(filename)


def getdata(filename, debug=0):
    """
    Load an ANA file and only return the data as a numpy array.

    data = pyana.getdata(filename)
    """
    return (fzread(filename, debug))['data']


def getheader(filename) -> str:
    """
    Load only the header (comment) of an ANA file.

    header = pyana.getheader(filename)
    """
    return fzhead(filename)


def fzwrite(filename, data, compress=1, comments=False, debug=0):
    """
    Save a 2d numpy array as an ANA file and return the bytes written, or NULL

    written = pyana.fzwrite(filename, data, compress=1, comments=False)
    """
    if comments:
        return _fzwrite(filename, data, compress, comments, debug)
    else:
        return _fzwrite(filename, data, compress, '', debug)


def writeto(filename, data, compress=1, comments=False, debug=0):
    """
    Similar as pyana.fzwrite().
    """
    return fzwrite(filename, data, compress, comments, debug)


# --- Selftesting using unittest starts below this line ---
class PyanaTests(unittest.TestCase):
    def setUp(self):
        # Create test images
        import numpy as n
        self.numpy = n
        self.img_size = (456, 345)
        self.img_src = n.arange(n.prod(self.img_size))
        self.img_src.shape = self.img_size
        self.img_i8 = self.img_src * 2 ** 8 / self.img_src.max()
        self.img_i8 = self.img_i8.astype(n.int8)
        self.img_i16 = self.img_src * 2 ** 16 / self.img_src.max()
        self.img_i16 = self.img_i16.astype(n.int16)
        self.img_i32 = self.img_src * 2 ** 16 / self.img_src.max()
        self.img_i32 = self.img_i32.astype(n.int32)
        self.img_i64 = self.img_src * 2 ** 16 / self.img_src.max()
        self.img_i64 = self.img_i64.astype(n.int64)
        self.img_f32 = self.img_src / self.img_src.max()
        self.img_f32 = self.img_f32.astype(n.float32)

    def runTests(self):
        unittest.TextTestRunner(verbosity=2).run(self.suite())

    def suite(self):
        return unittest.TestLoader().loadTestsFromTestCase(PyanaTests)

    def test_read_header(self):
        file = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'testfile.f0')
        header = fzhead(file)
        self.assertEqual(header, 'Time=1234567890')

    def _test_read(self):
        file = os.path.join(os.path.dirname(__file__), '..', 'testdata', 'testfile.f0')
        data = fzread(file)
        self.assertEqual(data['header']['header'], 'Time=1234567890')
        self.assertEqual(data['header']['size'], 1200000)
        self.assertEqual(data['data'].shape, (600, 1000))

    def testi8c(self):
        # Test int 8 compressed functions
        self._assert_rw("i8c", self.img_i8, compress=1)

    def testi8u(self):
        # Test int 8 uncompressed functions
        self._assert_rw("i8u", self.img_i8, compress=0)

    def testi16c(self):
        # Test int 16 compressed functions
        self._assert_rw("i16c", self.img_i16, compress=1)

    def testi16u(self):
        # Test int 16 uncompressed functions
        self._assert_rw("i16u", self.img_i16, compress=0)

    def testi32c(self):
        # Test int 32 compressed functions
        self._assert_rw("i32c", self.img_i32, compress=1)

    def testi32u(self):
        # Test int 32 uncompressed functions
        self._assert_rw("i32u", self.img_i32, compress=0)

    def testi64u(self):
        # Test int 64 uncompressed functions
        self._assert_rw("i64u", self.img_i64, compress=0)

    def testf32u(self):
        # Test float 32 uncompressed functions
        self._assert_rw("f32", self.img_f32, compress=0)

    def _assert_rw(self, name, frame, compress):
        # Store test frame, reread it and compare
        testfile = f'/tmp/{name}'
        if os.path.exists(testfile):
            os.remove(testfile)
        print("WRITING", testfile)
        fzwrite(testfile, frame, compress, False, 1)
        self.assertTrue(os.path.exists(testfile), msg=f"File {testfile} not created.")
        print("READING", testfile)
        result = fzread(testfile, 1)['data']
        print("ASSERTING")
        self.assertTrue(self.numpy.allclose(result, frame),
                        msg=f"Test {name} compression={compress} failed (diff: {self.numpy.sum(result - frame):g})")
        if os.path.exists(testfile):
            os.remove(testfile)

    def testf32c(self):
        # Test if float 32 compressed fails
        self.assertRaises(RuntimeError, fzwrite, '/tmp/f32c', self.img_f32, 1, 'testcase', 1)

    def testi64c(self):
        # Test if int 64 compressed fails
        self.assertRaises(RuntimeError, fzwrite, '/tmp/i64c', self.img_i64, 1, 'testcase', 1)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PyanaTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
