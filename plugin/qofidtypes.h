
#include <glib-object.h>

// I see no good way to avoid this
// - otherwise we have circular references
// - even though we do not need the full QofID type in QofInstance

/*  QofIdType declaration */
typedef const gchar * QofIdType;
/*  QofIdTypeConst declaration */
typedef const gchar * QofIdTypeConst;
/*  QofLogModule declaration */
typedef const gchar* QofLogModule;


