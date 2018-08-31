#include <Python.h>

// These are chunks of code that were the main hotspots that
// turned up in cProfile

/*
unsigned long long
C_bitfield_rotate_face_90(unsigned long long bitfield) {

    return ((((bitfield >> 12) & 0xF) << 60) | // c30 -> c00
           (((bitfield >> 28) & 0xF) << 56) | // c20 -> c01
           (((bitfield >> 44) & 0xF) << 52) | // c10 -> c02
           (((bitfield >> 60) & 0xF) << 48) | // c00 -> c03

           (((bitfield >>  8) & 0xF) << 44) | // c31 -> c10
           (((bitfield >> 24) & 0xF) << 40) | // c21 -> c11
           (((bitfield >> 40) & 0xF) << 36) | // c11 -> c12
           (((bitfield >> 56) & 0xF) << 32) | // c01 -> c13

           (((bitfield >>  4) & 0xF) << 28) | // c32 -> c20
           (((bitfield >> 20) & 0xF) << 24) | // c22 -> c21
           (((bitfield >> 36) & 0xF) << 20) | // c12 -> c22
           (((bitfield >> 52) & 0xF) << 16) | // c02 -> c23

           (((bitfield >>  0) & 0xF) << 12) | // c33 -> c30
           (((bitfield >> 16) & 0xF) <<  8) | // c23 -> c31
           (((bitfield >> 32) & 0xF) <<  4) | // c13 -> c32
           (((bitfield >> 48) & 0xF) <<  0));   // c03 -> c33
}

static PyObject* bitfield_rotate_face_90(PyObject* self, PyObject* args)
{
    unsigned long long bitfield;

    if(!PyArg_ParseTuple(args, "K", &bitfield))
        return NULL;

    return PyLong_FromUnsignedLongLong(C_bitfield_rotate_face_90(bitfield));
}
*/


static PyObject*
ida_heuristic_states_step10_444(PyObject* self, PyObject* args)
{
    PyObject *cube;
    PyObject *centers_444;
    PyObject *cubie_state_object;
    PyObject *lt_state;
    unsigned long centers_444_size = 0;
    unsigned long cubie_index = 0;
    unsigned int UD_state = 0;
    unsigned int LR_state = 0;
    unsigned int FB_state = 0;
    const char *cubie_state = NULL;

    if (! PyArg_ParseTuple(args, "O!O!",
                           &PyList_Type, &cube,
                           &PyTuple_Type, &centers_444)) {
        return NULL;
    }

    centers_444_size = PyTuple_Size(centers_444);
    lt_state = PyList_New(0);

    for (unsigned long i = 0; i < centers_444_size; i++) {
        // PyTuple_GetItem does error checking, PyTuple_GET_ITEM does not
        cubie_index = PyLong_AsUnsignedLong(PyTuple_GET_ITEM(centers_444, i));
        cubie_state_object = PyList_GET_ITEM(cube, cubie_index);
        cubie_state = PyBytes_AS_STRING(PyUnicode_AsEncodedString(cubie_state_object, "utf-8", "Error ~"));

        PyList_Append(lt_state, cubie_state_object);

        switch(*cubie_state) {
        case 'U':
            UD_state = UD_state | 0x1;
            break;
        case 'L':
            LR_state = LR_state | 0x1;
            break;
        default:
            FB_state = FB_state | 0x1;
            break;
        }
        UD_state = UD_state << 1;
        LR_state = LR_state << 1;
        FB_state = FB_state << 1;
    }

    UD_state = UD_state >> 1;
    LR_state = LR_state >> 1;
    FB_state = FB_state >> 1;

    // lt_state = "".join(lt_state)
    lt_state = PyUnicode_Join(PyUnicode_New(0, 127), lt_state);

    return Py_BuildValue("(OIII)", lt_state, UD_state, LR_state, FB_state);
}


// Our Module's Function Definition struct
// We require this `NULL` to signal the end of our method
// definition
static PyMethodDef myMethods[] = {
    // { "bitfield_rotate_face_90", bitfield_rotate_face_90, METH_VARARGS, "Rotate a 4x4x4 bitfield 90 degrees" },
    { "ida_heuristic_states_step10_444", ida_heuristic_states_step10_444, METH_VARARGS, "Calc heurisitic states" },
    { NULL, NULL, 0, NULL }
};


// Our Module Definition struct
static struct PyModuleDef cLibrary = {
    PyModuleDef_HEAD_INIT,
    "cLibrary",
    "C Module for rubikscubennnsolver",
    -1,
    myMethods
};


// Initializes our module using our above struct
PyMODINIT_FUNC PyInit_cLibrary(void)
{
    return PyModule_Create(&cLibrary);
}
