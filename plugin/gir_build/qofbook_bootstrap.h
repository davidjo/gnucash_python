/********************************************************************\
 * qofbook.h -- Encapsulate all the information about a dataset.    *
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
/*  @addtogroup Object
    @{ */
/*  @addtogroup Book
    A QOF Book is a dataset.  It provides a single handle
    through which all the various collections of entities
    can be found.   In particular, given only the type of
    the entity, the collection can be found.

    Books also provide the 'natural' place to working with
    a storage backend, as a book can encapsulate everything
    held in storage.
    @{ */
/*  @file qofbook.h
 * @brief Encapsulate all the information about a dataset.
 *
 * @author Copyright (c) 1998, 1999, 2001, 2003 Linas Vepstas <linas@linas.org>
 * @author Copyright (c) 2000 Dave Peticolas
 */

#ifndef QOF_BOOK_H
#define QOF_BOOK_H

/* We only want a few things exported to Guile */
#ifndef SWIG

typedef struct _QofBookClass  QofBookClass;

//#include "qofid.h"
#include "qofidtype.h"
//#include "kvp_frame.h"
#include "qofinstance.h"

/* --- type macros --- */
#define QOF_TYPE_BOOK            (qof_book_get_type ())
#define QOF_BOOK(o)              \
     (G_TYPE_CHECK_INSTANCE_CAST ((o), QOF_TYPE_BOOK, QofBook))
#define QOF_BOOK_CLASS(k)        \
     (G_TYPE_CHECK_CLASS_CAST((k), QOF_TYPE_BOOK, QofBookClass))
#define QOF_IS_BOOK(o)           \
     (G_TYPE_CHECK_INSTANCE_TYPE ((o), QOF_TYPE_BOOK))
#define QOF_IS_BOOK_CLASS(k)     \
     (G_TYPE_CHECK_CLASS_TYPE ((k), QOF_TYPE_BOOK))
#define QOF_BOOK_GET_CLASS(o)    \
     (G_TYPE_INSTANCE_GET_CLASS ((o), QOF_TYPE_BOOK, QofBookClass))


// dirty dummy declaration of QofBackend
// its a pointer in the struct so what it is doesnt matter
//typedef unsigned long long QofBackend;
typedef void *QofBackend;

//typedef gint64 	time64;


typedef void (*QofBookDirtyCB) (QofBook *book, gboolean dirty, gpointer user_data);

/* Book structure */
struct _QofBook
{
    QofInstance   inst;     /* Unique guid for this book. */

    /* Boolean indicates that the session is dirty -- that is, it has
     * not yet been written out to disk after the last time the
     * backend ran commit_edit(). This is distinct from the inherited
     * QofInstance::dirty, which indicates that some persisitent
     * property of the book object itself has been edited and not
     * committed. Some backends write data out as part of
     * commit_edit() and so don't use this flag.
     */
    gboolean session_dirty;

    /* The time when the book was first dirtied.  This is a secondary
     * indicator. It should only be used when session_saved is FALSE. */
    time64 dirty_time;

    /* This callback function is called any time the book dirty flag
     * changes state. Both clean->dirty and dirty->clean transitions
     * trigger a callback. */
    QofBookDirtyCB dirty_cb;

    /* This is the user supplied data that is returned in the dirty
     * callback function.*/
    gpointer dirty_data;

    /* The entity table associates the GUIDs of all the objects
     * belonging to this book, with their pointers to the respective
     * objects.  This allows a lookup of objects based on thier guid.
     */
    GHashTable * hash_of_collections;

    /* In order to store arbitrary data, for extensibility, add a table
     * that will be used to hold arbitrary pointers.
     */
    GHashTable *data_tables;

    /* Hash table of destroy callbacks for the data table. */
    GHashTable *data_table_finalizers;

    /* Boolean indicates whether book is safe to write to (true means
     * that it isn't). The usual reason will be a database version
     * mismatch with the running instance of Gnucash.
     */
    gboolean read_only;

    /* state flag: 'y' means 'open for editing',
     * 'n' means 'book is closed'
     * xxxxx shouldn't this be replaced by the instance editlevel ???
     */
    char book_open;

    /* a flag denoting whether the book is closing down, used to
     * help the QOF objects shut down cleanly without maintaining
     * internal consistency.
     * XXX shouldn't this be replaced by instance->do_free ???
     */
    gboolean shutting_down;

    /* version number, used for tracking multiuser updates */
    gint32  version;

    /* To be technically correct, backends belong to sessions and
     * not books.  So the pointer below "really shouldn't be here",
     * except that it provides a nice convenience, avoiding a lookup
     * from the session.  Better solutions welcome ... */
    QofBackend *backend;
};

struct _QofBookClass
{
    QofInstanceClass parent_class;
};

GType qof_book_get_type(void);

/*  @brief Encapsulates all the information about a dataset
 * manipulated by QOF.  This is the top-most structure
 * used for anchoring data.
 */


#endif /* SWIG */

#endif /* QOF_BOOK_H */
/*  @} */
/*  @} */
