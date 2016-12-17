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

/*  \brief QofBook reference */
typedef struct _QofBook       QofBook;

// because QofCollection refers to QofInstance the circular reference
// causes big problems for g-ir-scanner (functions left as functions not methods)
// dummy definition as for QofBook
typedef struct _QofCollection       QofCollection;

//#include "qofid.h"
#include "qofidtype.h"
#include "qofcollection.h"
#include "guid.h"
#include "gnc-date.h"
#include "kvp_frame.h"
#include "qof-gobject.h"

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

struct QofInstance_s
{
    GObject object;

    QofIdType        e_type;		   /* <	Entity type */

    /* kvp_data is a key-value pair database for storing arbirtary
     * information associated with this instance.
     * See src/engine/kvp_doc.txt for a list and description of the
     * important keys. */
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
 *
 *  Return the GncGUID of this instance
 */
/*@ dependent @*/
const GncGUID * qof_instance_get_guid (QofInstance *inst);

/* 
 *  \deprecated Use qof_instance_get_guid instead.
 *  Works like qof_instance_get_guid, but returns NULL on NULL
 */
/*@ dependent @*/
const GncGUID * qof_entity_get_guid (QofInstance *inst);

/**
 * qof_instance_get_collection:
 *
 * Returns : (transfer none) : Return the collection this instance belongs to
 *
 *  Return the collection this instance belongs to
 */
/*@ dependent @*/
QofCollection* qof_instance_get_collection (QofInstance *inst);

/**
 * qof_instance_set_guid:
 *
 *  Set the GncGUID of this instance
 */
void qof_instance_set_guid (QofInstance *inst, const GncGUID *guid);

/**
 * qof_instance_copy_guid:
 *
 *  Copy the GncGUID from one instance to another.  This routine should
 *  be used with extreme caution, since GncGUID values are everywhere
 *  assumed to be unique.
 */
void qof_instance_copy_guid (gpointer to, gconstpointer from);

/**
 * qof_instance_guid_compare:
 *
 *  Compare the GncGUID values of two instances.  This routine returns 0
 *  if the two values are equal, <0 if the first is smaller than the
 *  second, or >0 if the second is smaller tan the first.
 */
gint qof_instance_guid_compare(QofInstance *ptr1, QofInstance *ptr2);

//QofIdType qof_instance_get_e_type (const QofInstance *inst);
//void qof_instance_set_e_type (QofInstance *ent, QofIdType e_type);

/**
 * qof_instance_get_slots:
 *
 * Returns : (transfer none) : Return the pointer to the kvp_data
 *
 *  Return the pointer to the kvp_data
 */
/*@ dependent @*/
KvpFrame* qof_instance_get_slots (const QofInstance *inst);
void qof_instance_set_editlevel(QofInstance *inst, gint level);
gint qof_instance_get_editlevel (QofInstance *ptr);
void qof_instance_increase_editlevel (QofInstance *ptr);
void qof_instance_decrease_editlevel (QofInstance *ptr);
void qof_instance_reset_editlevel (QofInstance *ptr);

/**
 * qof_instance_version_cmp:
 *
 *  Compare two instances, based on thier last update times.
 *  Returns a negative, zero or positive value, respectively,
 *  if 'left' is earlier, same as or later than 'right'.
 *  Accepts NULL pointers, NULL's are by definition earlier
 *  than any value.
 */
int qof_instance_version_cmp (const QofInstance *left, const QofInstance *right);

/**
 * qof_instance_get_destroying:
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
 * qof_instance_set_destroying:
 *
 *  Set the flag that indicates whether or not this object is about to
 *  be destroyed.
 *
 *  @param ptr The object whose flag should be set.
 *
 *  @param value The new value to be set for this object.
 */
void qof_instance_set_destroying (QofInstance *ptr, gboolean value);

/**
 * qof_instance_get_dirty_flag: (skip)
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
 *
 *  Return value of is_dirty flag
 */
#define qof_instance_is_dirty qof_instance_get_dirty
gboolean qof_instance_get_dirty (QofInstance *inst);

/**
 * qof_instance_set_dirty: (method)
 *
 *  \brief Set the dirty flag
 *
 * Sets this instance AND the collection as dirty.
*/
void qof_instance_set_dirty(QofInstance* inst);

/* reset the dirty flag */
/**
 * qof_instance_mark_clean: (method)
 */
void qof_instance_mark_clean (QofInstance *inst);

/**
 * qof_instance_get_infant: (method)
 */
gboolean qof_instance_get_infant(const QofInstance *inst);

/**
 * qof_instance_get_version:
 *
 *  Get the version number on this instance.  The version number is
 *  used to manage multi-user updates.
 */
gint32 qof_instance_get_version (QofInstance *inst);

/**
 * qof_instance_set_version:
 *
 *  Set the version number on this instance.  The version number is
 *  used to manage multi-user updates.
 */
void qof_instance_set_version (QofInstance *inst, gint32 value);
/**
 * qof_instance_copy_version:
 *
 *  Copy the version number on this instance.  The version number is
 *  used to manage multi-user updates.
 */
void qof_instance_copy_version (gpointer to, gconstpointer from);

/**
 * qof_instance_get_version_check:
 *
 *  Get the instance version_check number
 */
guint32 qof_instance_get_version_check (QofInstance *inst);
/**
 * qof_instance_set_version_check:
 *
 *  Set the instance version_check number
 */
void qof_instance_set_version_check (QofInstance *inst, guint32 value);
/**
 * qof_instance_copy_version_check:
 *
 *  copy the instance version_check number
 */
void qof_instance_copy_version_check (gpointer to, gconstpointer from);

/**
 * qof_instance_get_idata:
 *
 *  get the instance tag number
 *  used for kvp management in sql backends.
 */
guint32 qof_instance_get_idata (QofInstance *inst);
void qof_instance_set_idata(QofInstance *inst, guint32 idata);

/**
 * qof_instance_get_display_name: (method)
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
 *
 *  Does this object refer to a specific object
 */
gboolean qof_instance_refers_to_object(const QofInstance* inst, const QofInstance* ref);

/**
 * qof_instance_get_typed_referring_object_list:
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
