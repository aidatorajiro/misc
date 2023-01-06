#define PY_SSIZE_T_CLEAN
#include <Python/Python.h>

// ref: https://github.com/matplotlib/matplotlib/blob/1456f8738c1bc9c936f3c3e6382023d97d522c88/src/_macosx.m

// hope it's safe
typedef struct {
    PyObject_HEAD
    unsigned long long int somenumber;
    unsigned long long int* somepointer;
} MyObjectOne;

static PyObject*
MyObjectOne_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    MyObjectOne *self = (MyObjectOne*)type->tp_alloc(type, 0);
    self->somenumber = 0;
    self->somepointer = NULL;
    return (PyObject*)self;
}

static PyObject *
some_func(PyObject *self, PyObject *args) {
    return my_struct;
}

static PyMethodDef BridgesMethods[] = { 
    {"some_func", some_func, METH_VARARGS, "Hello world."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "bridges",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    BridgesMethods
};

static void
MyObjectOne_dealloc(MyObjectOne* self)
{
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
MyObjectOne_repr(FigureCanvas* self)
{
    return PyUnicode_FromFormat("Helloworld %s %s", 123, 456);
}

static int
MyObjectOne_init(MyObjectOne *self, PyObject *args, PyObject *kwds)
{
    PyObject *builtins = NULL,
             *super_obj = NULL,
             *super_init = NULL,
             *init_res = NULL,
             *wh = NULL;
    
    // super(MyObjectOne, self).__init__(*args, **kwargs)
    if (!(builtins = PyImport_AddModule("builtins"))  // borrowed.
            || !(super_obj = PyObject_CallMethod(builtins, "super", "OO", &FigureCanvasType, self))
            || !(super_init = PyObject_GetAttrString(super_obj, "__init__"))
            || !(init_res = PyObject_Call(super_init, args, kwds))) {
        goto exit;
    }

    return PyErr_Occurred() ? -1 : 0;
}

static PyTypeObject MyObjectOneType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "MyObjectOne",
    .tp_basicsize = sizeof(MyObjectOne),
    .tp_dealloc = (destructor)MyObjectOne_dealloc,
    .tp_repr = (reprfunc)MyObjectOne_repr,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_init = (initproc)MyObjectOne_init,
    .tp_new = (newfunc)MyObjectOne_new,
    .tp_doc = "A MyObjectOne object.",
    .tp_methods = (PyMethodDef[]){  // All docstrings are inherited.
        {"_show",
         (PyCFunction)MyObjectOne__show,
         METH_NOARGS},
        {"_raise",
         (PyCFunction)MyObjectOne__raise,
         METH_NOARGS},
        {"destroy",
         (PyCFunction)MyObjectOne_destroy,
         METH_NOARGS},
        {}  // sentinel
    },
};

static PyObject *SomeError;

PyMODINIT_FUNC
PyInit_bridges(void)
{
    PyObject *m;

    m = PyModule_Create(&moduledef);
    if (m == NULL)
        return NULL;

    SomeError = PyErr_NewException("bridges.error", NULL, NULL);
    Py_XINCREF(SomeError);

    if (PyModule_AddObject(m, "SomeError", SomeError) < 0 || !prepare_and_add_type(&MyObjectOneType, m)) {
        Py_XDECREF(SomeError);
        Py_CLEAR(SomeError);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}

// i think it can go wrong
/*
@interface Window : NSWindow
{   PyObject* manager;
}
- (Window*)initWithContentRect:(NSRect)rect styleMask:(unsigned int)mask backing:(NSBackingStoreType)bufferingType defer:(BOOL)deferCreation withManager: (PyObject*)theManager;
- (NSRect)constrainFrameRect:(NSRect)rect toScreen:(NSScreen*)screen;
- (BOOL)closeButtonPressed;
- (void)dealloc;
@end

~~ here some implementations ~~

typedef struct {
    PyObject_HEAD
    Window* window;
} MyObjectTwo;

// → Accessing MyObjectTwo causes SEGV!!! (because the macro can't properly manage the struct?)
*/



