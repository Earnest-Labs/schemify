# Schemify

Schemify is a POC tool for applying schema declarations to a database.
This is slightly different from applying _migrations_, like flyway,
node-db-migrate, and most other schema migration tools. Migrations are
effectively _deltas_, and in other systems all such deltas from the
original schema are stored and applied.

This is a problem because it spreads out the _declaration_ of the
database in an unintuitive way.

A _declaration_ is a description of the desired state of the database
schema. Schemify compares the declarations against the database,
builds the smallest _migration_ to get from the current state to the
desired state, and optionally applies those migrations.

# Current State

Schemify is barely a proof of concept; it compares table declarations
against an existing schema and can add tables or columns to tables. It
doesn't yet understand simple things like indexes and certainly not
complicated things like functions, custom types, or triggers. In
principle these things are just extensions of what's already present,
but it seems likely there will be some refactoring involved should we
decide to move ahead with this.

# Installation

Once this is getting built and deployed by a CI system, you should
be able to install it via:

```
pip install schemify
```

You can install from source by running:

```
./setup pytest test
./setup install
```

# Use

Run schemify to install a given schema:

```
schemify -H {db-host} -p {db-port} -U {db-user} -P {db-password} -d {db-database} \
         -v -s {schema-directory}
```

# Productizing Notes:

1. CI needs to build and deploy this to pypi.
2. Need to support functions, custom types, triggers, and renaming
   of :allthethings:.
3. A decision should be made whether the declarations should continue
   to be yaml files, or whether an investment should be made in
   parsing SQL so they can more naturally be written as `CREATE
   TABLE...` statements. It's important to note that SQL doesn't have
   a native way to express that a schema entity used to have a different
   name.
