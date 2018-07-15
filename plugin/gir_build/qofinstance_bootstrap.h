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

// NOTA BENE - circular references REALLY confuse the scanner
// NO QofBook references in the bootstrap!!
// NO QofCollection references in the bootstrap!!

// cant see usage of gnc-date.h or qof-gobject.h
// so commenting out

//#include "qofid.h"
#include "qofidtype.h"
//#include "qofcollection.h"
//#include "guid.h"
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


/* @} */
/* @} */
#endif /* QOF_INSTANCE_H */
