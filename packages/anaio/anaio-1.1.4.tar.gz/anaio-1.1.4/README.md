ANA.IO - A Python module for ANA f0 file I/O
==========================================

This is `anaio`, a Python module to perform file input and output operations
with the ANA f0 file format, originally developed by Robert Shine. This module
is mostly a wrapper around the slightly modified code of the IDL DLM library 
by Michiel van Noort. This library in turn borrows code from the old ANA 
routines.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

Installation
============

The easiest and recommended way is to install via `pip`:

```bash
$ pip install anaio
```

This module can be installed using the standard NumPy distutils. Therefore,
simply running

   python setup.py install

will install this module to the default installation location. Running

   python setup.py

will start an interactive installation process.


Usage
=============
Import it as usual
```python
import anaio
```

To read a file:
```python
anadata = anaio.fzread(filename)
```

which will return a dict with the data in `anadata['data']` and some meta info in `anadata['header']`.

To return only either the data or header, use `anaio.getdata()` or `anaio.getheader()` respectively.
The letter will also not read the data and therefore speed up the process if you are interested in the header only.

To write a file:
```python
anaio.fzwrite(filename, data):
``` 

or use `anaio.writeto()`, which is an alias to `fzwrite()`.

Version history
===============

20230301, v1.0.0:
   * Renamed to anaio to prepare publishing on pipy

20220926, v0.5.0:
   * Forked from Tim van Werkhoven's PyANA v0.4.3
   * Added support to read ana headers without the data. 
   * Added more test cases.

20090422, v0.4.0:
   * Fixed dimension problem, ANA and numpy expect dimensions in different 
     order

20090422, v0.3.3:
   * Made errors a little nicer to read & more understandable. 
   * Added pyana.writeto() wrapper for fzwrite, similar to pyfits.

20090331, v0.3.2:
   * Updated segfault fix in anadecrunch(). Illegal read beyond memory 
     allocation can be as much as 4 bytes in the worst case in 32-bit 
     decrunching (although this is rarely used).

20090327, v0.3.1:
   * Fixed a segfault error in anadecrunch(). Problem was pre-caching of a few 
     bytes of compressed data, however the malloc() used for the compressed 
     data did not have those few bytes extra, causing a 1 or 2 byte illegal 
     read. Normally this shouldn't be a problem, but sometimes (like when I 
     needed it) it is.

20090326, v0.3.0:
   * Old code had memory leaks, trying Michiel van Noort's improved code from 
     libf0, the IDL DLM library. Hopefully this works better.
   * Renamed functions to correspond with the (original) IDL functions.
     load() -> fzread() and save() -> fzwrite(). Parameters still the same.

20090218, v0.2.2:
   * Added file exists check before calling _pyana.load C-routine

## Contributions

Based on Tim van Werkhoven's original PyANA implementation.
A wrapper around Michiel van Noort's ANACompress library. 

Currently maintained by J. Hölken

## License 
MIT

## Repository / Code / Issuetracker:
https://gitlab.gwdg.de/hoelken/pyana