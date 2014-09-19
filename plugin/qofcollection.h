
#include <glib-2.0/glib-object.h>

#include "guid.h"

#include "qof-string-cache.h"

/*  QofIdType declaration */
typedef const gchar * QofIdType;
/*  QofIdTypeConst declaration */
typedef const gchar * QofIdTypeConst;
/*  QofLogModule declaration */
typedef const gchar* QofLogModule;

typedef struct QofCollection_s QofCollection;

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

void
qof_collection_destroy (QofCollection *col)
{
    CACHE_REMOVE (col->e_type);
    g_hash_table_destroy(col->hash_of_entities);
    col->e_type = NULL;
    col->hash_of_entities = NULL;
    col->data = NULL;   /** XXX there should be a destroy notifier for this */
    g_free (col);
}


G_DEFINE_BOXED_TYPE(QofCollection, qof_collection,  qof_collection_copy, qof_collection_destroy)

