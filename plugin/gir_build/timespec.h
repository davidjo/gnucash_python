
#include <glib-object.h>
#include <time.h>

/*
 * Many systems, including Microsoft Windows and BSD-derived Unixes
 * like Darwin, are retaining the int-32 typedef for time_t. Since
 * this stops working in 2038, we define our own:
 */
typedef gint64 time64;

/*  The Timespec is just like the unix 'struct timespec'
 * except that we use a 64-bit unsigned int to
 * store the seconds.  This should adequately cover dates in the
 * distant future as well as the distant past, as long as they're not
 * more than a couple dozen times the age of the universe
 * Values of this type can range from -9,223,372,036,854,775,808 to
 * 9,223,372,036,854,775,807.
 */
typedef struct timespec64 Timespec;

struct timespec64
{
    time64 tv_sec;
    glong tv_nsec;
};
