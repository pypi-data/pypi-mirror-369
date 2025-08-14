/*!
@brief A C extension for Python to read ana f0 files
@author Johannes Hoelken <hoelken@mps.mpg.com>
@author Tim van Werkhoven <t.i.m.vanwerkhoven@gmail.com>

Based on Michiel van Noort's IDL DLM library 'f0' which contains a cleaned up 
version of the original anarw routines.
*/

// Headers
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>               // For python extension
#include "numpy/arrayobject.h"    // For NumPy C-API
#include <sys/time.h>             // For timestamps
#include <time.h>                 // For timestamps
#include "anadecompress.h"
#include "anacompress.h"
#include "types.h"
#include "anarw.h"

// Prototypes
static PyObject *anaio_fzread(PyObject *self, PyObject *args);
static PyObject *anaio_fzhead(PyObject *self, PyObject *args);
static PyObject *anaio_fzwrite(PyObject *self, PyObject *args);

// Methods table for this module
static PyMethodDef AnaioMethods[] = {
    {"fzread",  anaio_fzread, METH_VARARGS, "Load an ANA F0 file."},
    {"fzhead",  anaio_fzhead, METH_VARARGS, "Load header of an ANA F0 file."},
    {"fzwrite", anaio_fzwrite, METH_VARARGS, "Save an ANA F0 file."},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_anaio",                 // must match the extension module name
    "ANA IO Reader/Writer",
    -1,
    AnaioMethods,
    NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit__anaio(void) {
    PyObject *m = PyModule_Create(&moduledef);
    if (m == NULL) return NULL;

    import_array();  // initialize NumPy C-API
    if (PyErr_Occurred()) {
        Py_DECREF(m);
        return NULL;
    }
    return m;
}

/*!
@brief load an ANA f0 file data and header
@param [in] filename
@return [out] dict with data and header, NULL on failure
*/
static PyObject *anaio_fzread(PyObject *self, PyObject *args) {
    // Function arguments
    char *filename;
    int debug = 0;

    // Init ANA IO variables
    char *header = NULL;          // ANA header (comments)
    uint8_t *anaraw = NULL;       // Raw data
    int nd = -1, type = -1, *ds, size = -1, d; // Various properties

    // Data manipulation
    PyArrayObject *anadata = NULL; // Final ndarray

    // Parse arguments
    if (!PyArg_ParseTuple(args, "s|i", &filename, &debug)) {
        return NULL;
    }

    // Read ANA file
    if (debug == 1)
        printf("anaio_fzread(): Reading in ANA file: %s\n", filename);
    anaraw = ana_fzread(filename, &ds, &nd, &header, &type, &size);

    if (anaraw == NULL) {
        PyErr_SetString(PyExc_ValueError, "In anaio_fzread: could not read ana file, data returned is NULL.");
        return NULL;
    }
    if (type == -1) {
        PyErr_SetString(PyExc_ValueError, "In anaio_fzread: could not read ana file, type invalid.");
        return NULL;
    }

    // Mold into numpy array
    npy_intp npy_dims_vla[/* nd is known at runtime, use VLA if your compiler supports it */ nd];
    npy_intp *npy_dims = npy_dims_vla;
    int npy_type; // NumPy datatype

    // Calculate total datasize
    if (debug == 1)
        printf("anaio_fzread(): Dimensions: ");
    for (d = 0; d < nd; d++) {
        if (debug == 1)
            printf("%d ", ds[d]);
        // ANA stores dimensions reversed
        npy_dims[nd - 1 - d] = (npy_intp)ds[d];
    }
    if (debug == 1)
        printf("\nanaio_fzread(): Datasize: %d\n", size);

    // Convert datatype from ANA type to NPY_* type
    switch (type) {
        case INT8:     npy_type = NPY_INT8;    break;
        case INT16:    npy_type = NPY_INT16;   break;
        case INT32:    npy_type = NPY_INT32;   break;
        case FLOAT32:  npy_type = NPY_FLOAT32; break;
        case FLOAT64:  npy_type = NPY_FLOAT64; break;
        case INT64:    npy_type = NPY_INT64;   break;
        default:
            PyErr_SetString(PyExc_ValueError, "In anaio_fzread: datatype of ana file unknown/unsupported.");
            return NULL;
    }
    if (debug == 1)
        printf("anaio_fzread(): Read %d bytes, %d dimensions\n", size, nd);

    // Create numpy array from the data
    anadata = (PyArrayObject*)PyArray_SimpleNewFromData(nd, npy_dims, npy_type, (void *)anaraw);
    if (anadata == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "In anaio_fzread: failed to create NumPy array.");
        return NULL;
    }

    // Make sure Python owns the data, so it will free the data after use
    PyArray_ENABLEFLAGS(anadata, NPY_ARRAY_OWNDATA);

    if (!PyArray_CHKFLAGS(anadata, NPY_ARRAY_OWNDATA)) {
        PyErr_SetString(PyExc_RuntimeError, "In anaio_fzread: unable to own the data, will cause memory leak. Aborting");
        Py_DECREF(anadata);
        return NULL;
    }

    // Return the data in a dict with some metainfo attached
    // NB: Use 'N' for PyArrayObject, to transfer ownership of the new reference.
    return Py_BuildValue("{s:N,s:{s:i,s:i,s:s}}",
                         "data", anadata,
                         "header",
                         "size", size,
                         "ndims", nd,
                         "header", header);
}

/*!
@brief load header of an ANA f0 file
@param [in] filename
@return [out] header, NULL on failure
*/
static PyObject *anaio_fzhead(PyObject *self, PyObject *args) {
    char *filename = NULL;
    // Parse arguments
    if (!PyArg_ParseTuple(args, "s", &filename)) {
        return NULL;
    }
    return Py_BuildValue("s", ana_fzhead(filename));
}

/*!
@brief save an ANA format image to disk
@param [in] filename Full path to write data to
@param [in] data Data to write (numpy array)
@param [in] compress Apply (Rice) compression or not
@param [in] header Add a header to the file (or use default)
@return number of bytes read on success, NULL pointer on failure
*/
static PyObject *anaio_fzwrite(PyObject *self, PyObject *args) {
    // Python function arguments
    char *filename = NULL;
    PyArrayObject *anadata;
    int compress = 1, debug = 0;
    char *header = NULL;

    // Processed data goes here
    PyObject *anadata_align = NULL;
    uint8_t *anadata_bytes = NULL;

    // ANA file writing
    int type, d;

    // Parse arguments from Python function
    if (!PyArg_ParseTuple(args, "sO!|isi", &filename, &PyArray_Type, &anadata, &compress, &header, &debug))
        return NULL;

    if (filename == NULL) {
        PyErr_SetString(PyExc_ValueError, "In anaio_fzwrite: invalid filename.");
        return NULL;
    }

    // If header is NULL, then set the comment to a default value
    if (header == NULL) {
        if (debug == 1) printf("anaio_fzwrite(): Setting default header\n");
        struct timeval tv_time;
        gettimeofday(&tv_time, NULL);
        struct tm *tm_time = gmtime(&tv_time.tv_sec);
        asprintf(&header, "#%-42s compress=%d date=%02d:%02d:%02d.%03ld\n",
                 filename,
                 compress,
                 tm_time->tm_hour, tm_time->tm_min, tm_time->tm_sec, (long)(tv_time.tv_usec / 1000));
    }
    if (debug == 1) printf("anaio_fzwrite(): Header: '%s'\n", header);

    // Convert datatype from NumPy type to ANA type, and verify that ANA supports it
    switch (PyArray_TYPE(anadata)) {
        case NPY_INT8:     type = INT8;    if (debug==1) printf("anaio_fzwrite(): Found type NPY_INT8\n");    break;
        case NPY_INT16:    type = INT16;   if (debug==1) printf("anaio_fzwrite(): Found type NPY_INT16\n");   break;
        case NPY_INT32:    type = INT32;   if (debug==1) printf("anaio_fzwrite(): Found type NPY_INT32\n");   break;
        case NPY_INT64:    type = INT64;   if (debug==1) printf("anaio_fzwrite(): Found type NPY_INT64\n");   break;
        case NPY_FLOAT32:  type = FLOAT32; if (debug==1) printf("anaio_fzwrite(): Found type NPY_FLOAT32\n"); break;
        case NPY_FLOAT64:  type = FLOAT64; if (debug==1) printf("anaio_fzwrite(): Found type NPY_FLOAT64\n"); break;
        default:
            PyErr_SetString(PyExc_ValueError, "In anaio_fzwrite: datatype cannot be stored as ANA file.");
            return NULL;
    }

    // Check if compression flag is sane
    if (compress == 1 && (type == FLOAT32 || type == FLOAT64 || type == INT64)) {
        PyErr_SetString(PyExc_RuntimeError, "In anaio_fzwrite: datatype requested cannot be compressed.");
        return NULL;
    }
    if (debug == 1)
        printf("anaio_fzwrite(): pyarray datatype is %d, ana datatype is %d\n",
               PyArray_TYPE(anadata), type);

    // Sanitize data: ensure C-contiguous, aligned, and read-only view if needed
    anadata_align = PyArray_FromArray(anadata, NULL, NPY_ARRAY_CARRAY_RO);
    if (anadata_align == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "In anaio_fzwrite: failed to align/convert input array.");
        return NULL;
    }

    // Get a pointer to the aligned data
    anadata_bytes = (uint8_t *)PyArray_BYTES((PyArrayObject*)anadata_align);

    // Get the number of dimensions and dimensions
    int nd = PyArray_NDIM((PyArrayObject*)anadata_align);
    int *dims = (int*)malloc((size_t)nd * sizeof(int));
    if (dims == NULL) {
        Py_DECREF(anadata_align);
        PyErr_NoMemory();
        return NULL;
    }
    npy_intp *npy_dims = PyArray_DIMS((PyArrayObject*)anadata_align);

    if (debug == 1) printf("anaio_fzwrite(): Dimensions: ");
    for (d = 0; d < nd; d++) {
        // ANA stores dimensions reversed
        dims[d] = (int)npy_dims[nd - 1 - d];
        if (debug == 1) printf(" %d", dims[d]);
    }
    if (debug == 1) printf("\nanaio_fzwrite(): Total is %d-dimensional\n", nd);

    // Write ANA file
    if (debug == 1) printf("anaio_fzwrite(): Compress: %d\n", compress);
    if (compress == 1)
        ana_fcwrite(anadata_bytes, filename, dims, nd, header, type, 5);
    else
        ana_fzwrite(anadata_bytes, filename, dims, nd, header, type);

    free(dims);
    Py_DECREF(anadata_align);

    // If we didn't crash up to here, we're probably ok
    return Py_BuildValue("i", 1);
}
