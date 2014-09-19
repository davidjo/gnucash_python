
#include <string.h>
#include "guid.h"

/*  QofIdType declaration */
typedef const gchar * QofIdType;
/*  QofIdTypeConst declaration */
typedef const gchar * QofIdTypeConst;
/*  QofLogModule declaration */
typedef const gchar* QofLogModule;

typedef struct QofCollection_s QofCollection;

#ifdef GI_QOFCOLLECTION
// another issue - this is a plain struct - need to make it a boxed type

#include <glib.h>

struct QofCollection_s
{
    QofIdType    e_type;
    gboolean     is_dirty;

    GHashTable * hash_of_entities;
    gpointer     data;       /* place where object class can hang arbitrary data */
};

QofCollection *
qof_collection_copy (QofCollection *col)
{
    // does copying collections make sense??
    // this is complicated - we need to copy the hash table
    QofCollection *newcol;
    newcol = g_new0(QofCollection, 1);
    newcol->e_type = col->e_type;
    newcol->hash_of_entities = guid_hash_table_new();
    newcol->data = NULL;
    return newcol;
}


G_DEFINE_BOXED_TYPE(QofCollection, qof_collection,  qof_collection_copy, qof_collection_destroy)

