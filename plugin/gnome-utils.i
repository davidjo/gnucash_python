%module gnome_utils_c
%{
/* Includes the header in the wrapper code */
#include <config.h>

#include <glib.h>

#include "../../gnome-utils/gnc-main-window.h"

#include "../../gnome-utils/gnc-plugin-page.h"

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

%include "../../gnome-utils/gnc-main-window.h"

%include "../../gnome-utils/gnc-plugin-page.h"


#if defined(SWIGPYTHON)

#endif
