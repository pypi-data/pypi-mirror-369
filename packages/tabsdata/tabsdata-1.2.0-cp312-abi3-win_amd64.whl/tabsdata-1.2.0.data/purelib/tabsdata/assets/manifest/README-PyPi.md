<!--
Copyright 2025 Tabs Data Inc.
-->

![Tabsdata](https://docs.tabsdata.com/tabsdata.png)

<div align="center">
    <a href="https://tabsdata.com">Tabsdata</a> |
    <a href="https://docs.tabsdata.com/1.2.0/guide/intro.html">User Guide</a> |
    <a href="https://docs.tabsdata.com/1.2.0/api_ref/index.html">API Reference</a>
</div>

# License

Your use of this product is subject to the terms of use available at https://tabsdata.com/license.

# Tabsdata Pub/Sub for Tables

[Tabsdata](https://tabsdata.com) is a publish-subscribe (pub/sub) server for tables.

Tabsdata has connectors to publish and subscribe tables from local files, S3, Azure Storage,
MySQL/MariaDB, Oracle, PostgreSQL. It also provides a Connector Plugin API to write custom
connectors.

Tables can populated with external data or using data from other tables already existing
in the Tabsdata server.

Tables can be manipulated using a [TableFrame API](https://docs.tabsdata.com/latest/api_ref/index.html)
(internally Tabsdata uses [Polars](https://github.com/pola-rs/polars)) that enables selection,
filtering, aggregation and joins operations.

For more details refer
to [Tabsdata Getting Started](https://docs.tabsdata.com/latest/guide/02_getting_started/main.html)
(latest) or the [Tabsdata User Guide](https://docs.tabsdata.com/latest/guide/intro.html) (latest).

## Installation

Supported platforms:

* Windows (x86 - latest)
* macOS (Apple silicon/x86 - latest)
* Ubuntu, Debian & RedHat - (x86 - latest)

```
pip install tabsdata
```

## This version (1.2.0) Documentation

* [User Guide](https://docs.tabsdata.com/1.2.0/guide/intro.html)
* [API Reference](https://docs.tabsdata.com/1.2.0/api_ref/index.html)

## How Does Tabsdata Work?

The following snippets show how to publish and subscribe to tables in Tabsdata.

### Publishing data from a MySQL Database

```
@td.publisher(
    td.MySQLSource(
        "mysql://127.0.0.1:3306/testing",
        ["select * from CUSTOMERS"],
        td.UserPasswordCredentials("admin", td.EnvironmentSecret("DB_PASWORD"))
    ),
    tables=["customers"]
)
def customers_publisher(customers: td.TableFrame) -> td.TableFrame:
    return customers
```

### Subscribing, transforming and publishing data within Tabsdata

```
@td.transformer(
    input_tables=["persons"],
    output_tables=["spanish"]
)
def tfr(persons: td.TableFrame):
    return persons.filter(td.col("nationality").eq("spanish")).select(
        ["identifier", "name", "surname", "language"]
    )
```

### Subscribing to data in an S3 Bucket

```
@td.subscriber(
    "spanish",
    td.S3Destination(
        "s3://my_bucket/spanish.parquet",
        td.S3AccessKeyCredentials(
            td.EnvironmentSecret("AWS_ACCESS_KEY_ID"),
            td.EnvironmentSecret("AWS_SECRET_KEY")
        )
    ),
)
def sub(spanish: td.TableFrame):
    return spanish
```

### Executing the Publisher

To publish data to Tabsdata run the following command:

```
$ td fn trigger --coll examples --name pub
```

Every time the `pub` publisher is executed, the `tfr` transformer and the `sub` subscriber will also be
executed.
