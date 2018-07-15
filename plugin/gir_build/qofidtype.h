
#include <glib-object.h>

#ifndef QOF_IDTYPE_H
#define QOF_IDTYPE_H

// I see no good way to avoid this
// - otherwise we have circular references
// - even though we do not need the full QofID type in QofInstance

/*  QofIdType declaration */
typedef const gchar * QofIdType;
/*  QofIdTypeConst declaration */
typedef const gchar * QofIdTypeConst;
/*  QofLogModule declaration */
typedef const gchar* QofLogModule;

//typedef struct QofCollection_s QofCollection;

//#include "qofinstance.h"

#define QOF_ID_NONE           NULL
#define QOF_ID_NULL           "null"

#define QOF_ID_BOOK           "Book"
#define QOF_ID_SESSION        "Session"

#endif /* QOF_IDTYPE_H */
