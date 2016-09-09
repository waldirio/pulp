Introduction
============

The pulp 3 data modeling effort is not just a translation or porting effort but instead
an effort to build pulp 3 using pulp 2.  Remodeling will include changes to leverage the
relational capabilities of postgres but also to improve upon the pulp 2 model.

When creating each pulp 3 model object, consider the following:

- Understand what the pulp 2 model (collection) stores and how the information
  is used by pulp.

- Name the model/table appropriately.  A table is implicitly plural.  Naming a
  table `repository` is more appropriate than `repositories`.

- Name the model class appropriately.  Each model object is a row in the table
  an not a collection.  Class names should be singular.  For example, `Repository`
  is a more appropriate class name than `Repositories`.

- Do not use multiple inheritance (mixins) unless there is no other choice. Although
  they are convenient, they greatly diminish the clarity of the model and as with
  multiple inheritance in general, can result in untended behavior.  With a little extra
  effort, a proper class hierarchy is almost aways possible and will be better in the end.

- Question all fields.  Both the existence, type and naming.  Field names beginning with `_` 
  should not exist in pulp 3.  The primary key field name is `id` and already defined in the
  `Model` base class.  All `display_name` fields need to be renamed to `name`.  Also, avoid
  redundant scope by prefixing field names (or any attribute) with the name of the class.
  For example: `Task.task_type`.

- Question all methods (including @property). We **only** want those methods that encapsulate
  significant complexity and are widely used.  Most of the methods on pulp 2 models will likely
  not be necessary or wanted in the pulp 3 models.  Let's keep the model interface as clean
  as possible.

- Most string fields will be `TextField`.  When the field is required and indexed,
  use: `TextField(db_index=True)`.  When required but **not** indexed, 
  use: `TextField(blank=False, default=None)`.  This ensures integrity at the model and
  database layer(s) and supports validation at the REST layer.

- All fields containing *ISO-8601* strings must be converted to `DateTimeField`.

- Think about *natural* keys.  For example, each repository has a unique name (instead of repo_id
  like in pulp 2) that is known to users and is not the primary key (`id` is).  The `name` is
  the *natural* key.  Don't forget the index. See: https://en.wikipedia.org/wiki/Natural_key

- Define a `natrual_key()` method in each model.  This both documents the *natural* key and
  will be used by the django serializer.
  See: https://docs.djangoproject.com/en/1.8/topics/serialization/#serialization-of-natural-keys

- For consistency, please format your docblock using the existing models as an example.

- Each *public* model class is exposed in the `models`.  Add them to `models.__init__.py`.
  All model classes should be imported from the `pulp.platform.models` package and not from
  the module directly.


Development Process
===================

- The *refactor* tasks (in Redmine) group related collections.

- The pulp 3 models are grouped into modules within the `models` package.

- Foreach model class defined, A *refactor* task needs to be created in Redmine for
  migrating the data.  See existing examples.
  
- Foreach model class defined, add a section to the *Notes* section below.

- Add unit tests for models.  Only methods encapsulating complexity need tests.
  In addition to this, add a set of *howto* tests to demonstrate common use cases for the
  model.  They are intended to provide an example to developers and sanity testing only.
  100% coverage is not expected.  Also, we don't need to test django itself.
  

Notes About Models
==================

This section captures notes about each model.  Developers should explain differences
between the pulp 2 and pulp 3.  This is a good place to give examples of how models are intended
to be used or extended by plugins.  Except for how to extend a class, refer to the *howto* unit
tests instead of including code blocks here.

Consumer
--------

The consumer models are much like that in pulp 2 except the fields related to the removed
*nodes* and *agent* functionality are gone.  The `bind` has be replaced with a simple relation
that is managed by django because no addition fields on the join table are needed.

The *applicability* models/tables have not been included because *applicability* is not a generic
platform concept.  Errata and RPM applicability is owned by the RPM plugin.  That said,
the `ConsumerContent` model provides a base class for plugins to model content that is installed
on a consumer.

Repository
----------

The repository models include importers and distributors.  The main difference being the
consolidation of the importer and distributor and it's configuration.  In the model, a
`Plugin` is the base for plugin contributed models that can be associated to a repository.
On importer and distributor base models, the *standard* configuration settings that were
separate documents in pulp 2 are attributes of the importer and distributor itself.  These models
follow the *master-detail* pattern.  Plugins needing additional configuration, need to extend the
base model (master) and add the extra fields on a new (detail) model.

Examples:

```
Class MyImporter(RepositoryImporter):

    field_1 = models.TextField()
    field_2 = models.TextField()

    class Meta:
        unique_together = ()
```

Content
-------
