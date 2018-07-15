/********************************************************************\
 * qofinstance.h -- fields common to all object instances           *
 *                                                                  *
 * This program is free software; you can redistribute it and/or    *
 * modify it under the terms of the GNU General Public License as   *
 * published by the Free Software Foundation; either version 2 of   *
 * the License, or (at your option) any later version.              *
 *                                                                  *
 * This program is distributed in the hope that it will be useful,  *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of   *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the    *
 * GNU General Public License for more details.                     *
 *                                                                  *
 * You should have received a copy of the GNU General Public License*
 * along with this program; if not, contact:                        *
 *                                                                  *
 * Free Software Foundation           Voice:  +1-617-542-5942       *
 * 51 Franklin Street, Fifth Floor    Fax:    +1-617-542-2652       *
 * Boston, MA  02110-1301,  USA       gnu@gnu.org                   *
 *                                                                  *
\********************************************************************/
/*  @addtogroup Entity
    @{ */
/*  @addtogroup Instance
    Qof Instances are a derived type of QofInstance.  The Instance
    adds some common features and functions that most objects
    will want to use.

    @{ */
/*  @file qofinstance.h
 *  @brief Object instance holds common fields that most gnucash objects use.
 *
 *  @author Copyright (C) 2003,2004 Linas Vepstas <linas@linas.org>
 *  @author Copyright (c) 2007 David Hampton <hampton@employees.org>
 */

#ifndef QOF_INSTANCE_H
#define QOF_INSTANCE_H

typedef struct _QofInstanceClass QofInstanceClass;
typedef struct QofInstance_s QofInstance;

// now thats interesting - because the gir scanner actually creates an object
// from the include file it is able to extract data from the in memory gobject
// - primarily any private data defined - without accessing the c file!!
// this means any type in the private data we need to define here
// so we DO need a QofBook gir - else the private QofBook is a bit undefined
// if we just use the QofBook reference here
// - except we cant because the QofBook needs a QofInstance definition
// so leave as below and patch

/*  \brief QofBook reference */
typedef struct _QofBook       QofBook;

// because QofCollection refers to QofInstance the circular reference
// causes big problems for g-ir-scanner (functions left as functions not methods)
// dummy definition as for QofBook
typedef struct _QofCollection       QofCollection;

// cant see usage of gnc-date.h or qof-gobject.h
// so commenting out

//#include "qofid.h"
#include "qofidtype.h"
//#include "qofcollection.h"
#include "guid.h"
//#include "gnc-date.h"
//#include "qof-gobject.h"

/* --- type macros --- */
#define QOF_TYPE_INSTANCE            (qof_instance_get_type ())
#define QOF_INSTANCE(o)              \
     (G_TYPE_CHECK_INSTANCE_CAST ((o), QOF_TYPE_INSTANCE, QofInstance))
#define QOF_INSTANCE_CLASS(k)        \
     (G_TYPE_CHECK_CLASS_CAST((k), QOF_TYPE_INSTANCE, QofInstanceClass))
#define QOF_IS_INSTANCE(o)           \
     (G_TYPE_CHECK_INSTANCE_TYPE ((o), QOF_TYPE_INSTANCE))
#define QOF_IS_INSTANCE_CLASS(k)     \
     (G_TYPE_CHECK_CLASS_TYPE ((k), QOF_TYPE_INSTANCE))
#define QOF_INSTANCE_GET_CLASS(o)    \
     (G_TYPE_INSTANCE_GET_CLASS ((o), QOF_TYPE_INSTANCE, QofInstanceClass))
#ifndef __KVP_FRAME
typedef struct KvpFrameImpl KvpFrame;
#define __KVP_FRAME
#endif

struct QofInstance_s
{
    GObject object;
    QofIdType        e_type;		   /* <	Entity type */
    KvpFrame *kvp_data;
};

struct _QofInstanceClass
{
    GObjectClass parent_class;

    /* Returns a displayable string to represent this object */
    gchar* (*get_display_name)(const QofInstance* inst);

    /* Does this object refer to a specific object */
    gboolean (*refers_to_object)(const QofInstance* inst, const QofInstance* ref);

    /* Returns a list of my type of object which refers to an object */
    GList* (*get_typed_referring_object_list)(const QofInstance* inst, const QofInstance* ref);
};

/**
 * qof_instance_get_type:
 *
 *  Return the GType of a QofInstance
 */
GType qof_instance_get_type(void);

/**
 * qof_instance_init_data: (method)
 *
 *  Initialise the settings associated with an instance
 */
void qof_instance_init_data (QofInstance *inst, QofIdType type, QofBook *book);

/**
 * qof_instance_get_book: (method)
 * @inst : (type Qof.Instance) :
 *
 * Returns : (transfer none) : Return the book pointer
 *
 *  Return the book pointer
 */
/*@ dependent @*/
QofBook *qof_instance_get_book (QofInstance *inst);

/**
 * qof_instance_set_book: (method)
 * @inst : (type Qof.Instance) :
 *
 *  Set the book pointer
 */
void qof_instance_set_book (QofInstance *inst, QofBook *book);

/**
 * qof_instance_copy_book:
 *
 *  Copy the book from one QofInstances to another.
 */
void qof_instance_copy_book (gpointer *ptr1, gconstpointer *ptr2);

/**
 * qof_instance_books_equal:
 *
 *  See if two QofInstances share the same book.
 */
gboolean qof_instance_books_equal (QofInstance *ptr1, QofInstance *ptr2);

/**
 * qof_instance_get_guid:
 * @inst : (type Qof.Instance) :
 *
 *  Return the GncGUID of this instance
 */
/*@ dependent @*/
const GncGUID * qof_instance_get_guid (QofInstance *inst);

/**
 * qof_entity_get_guid:
 * @inst : (type Qof.Instance) :
 * return : (transfer none) :
 *
 *  \deprecated Use qof_instance_get_guid instead.
 *  Works like qof_instance_get_guid, but returns NULL on NULL
 */
/*@ dependent @*/
const GncGUID * qof_entity_get_guid (QofInstance *inst);

/**
 * qof_instance_get_collection:
 * @inst : (type Qof.Instance) :
 *
 * Returns : (transfer none) : Return the collection this instance belongs to
 *
 *  Return the collection this instance belongs to
 */
/*@ dependent @*/
QofCollection* qof_instance_get_collection (QofInstance *inst);

/**
 * qof_instance_guid_compare:
 *
 *  Compare the GncGUID values of two instances.  This routine returns 0
 *  if the two values are equal, <0 if the first is smaller than the
 *  second, or >0 if the second is smaller tan the first.
 */
gint qof_instance_guid_compare(QofInstance *ptr1, QofInstance *ptr2);

gint qof_instance_get_editlevel (gconstpointer ptr);

/**
 * qof_instance_version_cmp:
 *
 *  Compare two instances, based on their last update times.
 *  Returns a negative, zero or positive value, respectively,
 *  if 'left' is earlier, same as or later than 'right'.
 *  Accepts NULL pointers, NULL's are by definition earlier
 *  than any value.
 */
int qof_instance_version_cmp (const QofInstance *left, const QofInstance *right);

/**
 * qof_instance_get_destroying:
 * @ptr : (type Qof.Instance) :
 *
 *  Retrieve the flag that indicates whether or not this object is
 *  about to be destroyed.
 *
 *  @param ptr The object whose flag should be retrieved.
 *
 *  @return TRUE if the object has been marked for destruction. FALSE
 *  if the object is not marked for destruction, or if a bad parameter
 *  is passed to the function.
 */
gboolean qof_instance_get_destroying (QofInstance *ptr);

/**
 * qof_instance_get_dirty_flag: (skip)
 * @ptr : (type Qof.Instance) :
 *
 *  Retrieve the flag that indicates whether or not this object has
 *  been modified.  This is specifically the flag on the object. It
 *  does not perform any other checking which might normally be
 *  performed when testing to see if an object is dirty.  If there is
 *  any question, use the qof_instance_is_dirty() function instead.
 *
 *  @param ptr The object whose flag should be retrieved.
 *
 *  @return TRUE if the object has been modified and not saved. FALSE
 *  if the object has not been modified, or if a bad parameter is
 *  passed to the function.
 */
gboolean qof_instance_get_dirty_flag (QofInstance *ptr);

void qof_instance_print_dirty (const QofInstance *entity, gpointer dummy);

/**
 * qof_instance_get_dirty: (method)
 * @inst : (type Qof.Instance) :
 *
 *  Return value of is_dirty flag
 */
#define qof_instance_is_dirty qof_instance_get_dirty
gboolean qof_instance_get_dirty (QofInstance *inst);

/**
 * qof_instance_get_infant: (method)
 * @inst : (type Qof.Instance) :
 *
 */
gboolean qof_instance_get_infant(const QofInstance *inst);

/**
 * qof_instance_get: (method)
 * @inst : (type Qof.Instance) :
 *
 * \brief Wrapper for g_object_get
 */
void qof_instance_get (const QofInstance *inst, const gchar *first_param, ...);

/**
 * qof_instance_set: (method)
 * @inst : (type Qof.Instance) :
 *
 * \brief Wrapper for g_object_set
 * Group setting multiple parameters in a single begin/commit/rollback
 */
void qof_instance_set (QofInstance *inst, const gchar *first_param, ...);

/**
 * qof_instance_get_idata:
 * @inst : (type Qof.Instance) :
 *
 *   get the instance tag number
    used for kvp management in sql backends.
 */
guint32 qof_instance_get_idata (gconstpointer inst);

/**
 * qof_instance_get_display_name: (method)
 * @inst : (type Qof.Instance) :
 *
 * Returns a displayable name for this object.  The returned string must be freed by the caller.
 */
gchar* qof_instance_get_display_name(const QofInstance* inst);

/**
 * qof_instance_get_referring_object_list: (method)
 * @inst: (type Qof.Instance) : object
 *
 * Returns : (element-type *guint64) (transfer container): Returns a list of objects which refer to a specific object.  The list must be freed by the caller,
 * but the objects on the list must not.
 *
 * Returns a list of objects which refer to a specific object.  The list must be freed by the caller,
 * but the objects on the list must not.
 */
GList* qof_instance_get_referring_object_list(const QofInstance* inst);

/**
 * qof_instance_refers_to_object:
 * @inst : (type Qof.Instance) :
 *
 *  Does this object refer to a specific object
 */
gboolean qof_instance_refers_to_object(const QofInstance* inst, const QofInstance* ref);

/**
 * qof_instance_get_typed_referring_object_list:
 * @inst : (type Qof.Instance) :
 *
 * Returns : (element-type *guint64) (transfer container): Returns a list of my type of object which refers to an object.  For example, when called as
 *      qof_instance_get_typed_referring_object_list(taxtable, account);
 *
 *  Returns a list of my type of object which refers to an object.  For example, when called as
 *      qof_instance_get_typed_referring_object_list(taxtable, account);
 *  it will return the list of taxtables which refer to a specific account.  The result should be the
 *  same regardless of which taxtable object is used.  The list must be freed by the caller but the
 *  objects on the list must not.
 */
GList* qof_instance_get_typed_referring_object_list(const QofInstance* inst, const QofInstance* ref);

/**
 * qof_instance_get_referring_object_list_from_collection:
 *
 * Returns : (element-type *guint64) (transfer container): Returns a list of objects from the collection which refer to the specific object.  The list must be
    freed by the caller but the objects on the list must not.
 *
 *  Returns a list of objects from the collection which refer to the specific object.  The list must be
 *  freed by the caller but the objects on the list must not.
 */
GList* qof_instance_get_referring_object_list_from_collection(const QofCollection* coll, const QofInstance* ref);

/* @} */
/* @} */
#endif /* QOF_INSTANCE_H */
