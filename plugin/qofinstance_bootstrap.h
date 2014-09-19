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


#ifdef GI_QOFIDTYPE

#include <glib-object.h>

// I see no good way to avoid this
// - otherwise we have circular references
// - even though we do not need the full QofID type in QofInstance
// great - only direct addition fixes issue
// - including a file with these definitions in still leads to Unresolve type
// actually defining here has no effect now we have removed explicit usage
// of QofBook type in this file
// - as in this case a GProperty is is declared to store the book object
//typedef void QofBook;

/*  QofIdType declaration */
typedef const gchar * QofIdType;
/*  QofIdTypeConst declaration */
typedef const gchar * QofIdTypeConst;
/*  QofLogModule declaration */
typedef const gchar* QofLogModule;

#else

#include "qofid.h"

#endif


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

    QofIdType        e_type;		   /*<	Entity type */

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
 *  Return the GType of a QofInstance
 */
GType qof_instance_get_type(void);

#endif /* QOF_INSTANCE_H */
