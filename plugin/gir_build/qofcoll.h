
/*  QofCollection declaration

@param e_type QofIdType
@param is_dirty gboolean
@param hash_of_entities GHashTable
@param data gpointer, place where object class can hang arbitrary data

*/

/*  @name Collections of Entities
 @{ */

/**
 * qof_collection_new:
 *
 * Returns : (transfer full)
 *
 *   create a new collection of entities of type
 */
QofCollection * qof_collection_new (QofIdType type);

/**
 * qof_collection_count:
 *
 *  return the number of entities in the collection.
 */
guint qof_collection_count (const QofCollection *col);

/**
 * qof_collection_destroy:
 *
 *  destroy the collection
 */
void qof_collection_destroy (QofCollection *col);

/**
 * qof_collection_get_type:
 *
 *  return the type that the collection stores
 */
QofIdType qof_collection_get_type (const QofCollection *col);

/**
 * qof_collection_lookup_entity:
 *
 * Returns : (transfer none)
 *
 *  Find the entity going only from its guid
 */
/*@ dependent @*/
QofInstance * qof_collection_lookup_entity (const QofCollection *col, const GncGUID *guid);

/* 
 *  Callback type for qof_collection_foreach
 */
typedef void (*QofInstanceForeachCB) (QofInstance *inst, gpointer user_data);

/**
 * qof_collection_foreach:
 * @col:
 * @cb : (scope call)
 * @user_data:
 *
 *  Call the callback for each entity in the collection.
 */
void qof_collection_foreach (const QofCollection *col, QofInstanceForeachCB cb,
                             gpointer user_data);

/**
 * qof_collection_get_data:
 *
 *  Store and retreive arbitrary object-defined data
 *
 * XXX We need to add a callback for when the collection is being
 * destroyed, so that the user has a chance to clean up anything
 * that was put in the 'data' member here.
 */
gpointer qof_collection_get_data (const QofCollection *col);
void qof_collection_set_data (QofCollection *col, gpointer user_data);

/**
 * qof_collection_is_dirty:
 * 
 * Return value of 'dirty' flag on collection
 */
gboolean qof_collection_is_dirty (const QofCollection *col);

/*  @name QOF_TYPE_COLLECT: Linking one entity to many of one type

\note These are \b NOT the same as the main collections in the book.

QOF_TYPE_COLLECT is a secondary collection, used to select entities
of one object type as references of another entity.
\sa QOF_TYPE_CHOICE.

@{
*/
/*  \brief Add an entity to a QOF_TYPE_COLLECT.

\note These are \b NOT the same as the main collections in the book.

Entities can be
freely added and merged across these secondary collections, they
will not be removed from the original collection as they would
by using ::qof_instance_insert_entity or ::qof_instance_remove_entity.

*/
gboolean
qof_collection_add_entity (QofCollection *coll, QofInstance *ent);

void qof_collection_remove_entity (QofInstance *ent);

/*  \brief Compare two secondary collections.

Performs a deep comparision of the collections. Each QofInstance in
each collection is looked up in the other collection, via the GncGUID.

\return 0 if the collections are identical or both are NULL
otherwise -1 if target is NULL or either collection contains an entity with an invalid
GncGUID or if the types of the two collections do not match,
or +1 if merge is NULL or if any entity exists in one collection but
not in the other.
*/
gint
qof_collection_compare (QofCollection *target, QofCollection *merge);

/*  \brief Create a secondary collection from a GList

@param type The QofIdType of the QofCollection \b and of
	\b all entities in the GList.
@param glist GList of entities of the same QofIdType.

@return NULL if any of the entities fail to match the
	QofCollection type, else a pointer to the collection
	on success.
*/
/**
 * qof_collection_from_glist:
 * @type:
 * @glist: (element-type *guint64)
 *
 * Returns : (transfer full)
 *
 */
QofCollection*
qof_collection_from_glist (QofIdType type, const GList *glist);

/*  @} */
