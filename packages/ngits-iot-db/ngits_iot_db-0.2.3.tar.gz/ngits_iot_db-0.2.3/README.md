database uri
============

You can set database uri by setting `IOT_DATABASE_URL` variable.

```shell
export IOT_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/iot_local
```


make migrations
===============

```shell
alembic revision --autogenerate -m "Migration message."
```

upgrade
=======

```shell
# upgrade all
alembic upgrade head

# upgrade all to specific migration
alembic upgrade <revision_id>
```

downgrade
=========

```shell
# downgrade all
alembic downgrade base

# downgrade all to specific migration
alembic downgrade <revision_id>
```
