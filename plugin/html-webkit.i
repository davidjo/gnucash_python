%module html_webkit_c
%{
/* Includes the header in the wrapper code */
#include <config.h>

#include <webkitgtk-1.0/webkit/webkit.h>

#include "../../html/gnc-html.h"

#include "../../html/gnc-html-webkit.h"

%}

#if defined(SWIGGUILE)
%{
#include "engine-helpers-guile.h"
#include "guile-mappings.h"

SCM scm_init_sw_app_utils_module (void);
%}
#endif

#if defined(SWIGPYTHON)
%{
/* avoid no previous prototype warning/error */
#if PY_VERSION_HEX >= 0x03000000
PyObject*
#else
void
#endif
SWIG_init (void);
%}
#endif

%import "../../base-typemaps.i"

// including glib.h gives rise to errors
// define these here

#define G_BEGIN_DECLS
#define G_END_DECLS

// how do we rename variables in a structure??
// this is dangerous - applies to any occurrence of print??
%rename(_print) print;

%ignore gnc_html_get_embedded_param;

%include "./gnc-html.h"

%include "../../html/gnc-html-webkit.h"


#if defined(SWIGPYTHON)

#endif
