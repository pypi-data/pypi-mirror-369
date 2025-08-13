# echoss_db

---

MySQL, MongoDB, Opensearch compatible query access package

Version History:

- 1.1.0 : Add Scroll, Bulk functions in ElasticSearch
- 1.2.0 : change mysql base package to sqlalchemy (previous version use pymysql)

## Prepare

사용 전 config(인증 정보) 의 유무를 확인한 뒤 사용해야한다.
config file example:

```



mysql:
    user : <user_id>
    passwd : <pass code>
    host : <IP addrress or domain>
    port : :<network port number>
    db : <schema name>
    charset : utf8mb4

mongo:
    host : <IP addrress or domain>
    port :<network port number>
    db : <database name>

elastic:
    user : <user_id>
    passwd : <pass code>
    host : <IP addrress or domain>
    port : :<network port number>
    scheme : <http or https>
```

## Installaion

---

To install this package, please use Python 3.8 or higher.

```
    pip install -U echoss-db
```

## Quick Start

### Import package and class

```
    from echoss_db import MysqlQuery, MongoQuery, ElasticSearch

    mysql = MysqlQuery('CONFIG_FILE_PATH' or dict)
    mongo = MongoQuery('CONFIG_FILE_PATH' or dict)
    elastic = ElasticSearch('CONFIG_FILE_PATH' or dict)
```

### MySQL

---

```
    # CREATE
    mysql.create('QUERY_STRING')

    # DROP
    mysql.drop('QUERY_STRING')

    # TRUNCATE
    mysql.truncate('QUERY_STRING')

    # ALTER
    mysql.alter('QUERY_STRING')

    # SELECT
    mysql.select('QUERY_STRING', params=None) -> dataframe
    mysql.select_one('QUERY_STRING', params=None) -> dict
    mysql.select_list('QUERY_STRING', params=None) -> list(dict)
    mysql.faster_select('QUERY_STRING', params=None) -> dataframe

    # INSERT without params
    mysql.insert('QUERY_STRING', params=None) -> int
    # INSERT with tuple
    mysql.insert('QUERY_STRING', params) -> int
    # INSERT with list[tuple]
    mysql.insert('QUERY_STRING', params_list) -> int

    # UPDATE
    mysql.update('QUERY_STRING', params=None) -> int

    # DELETE
    mysql.delete('QUERY_STRING', params=None) -> int

    # show Database
    mysql.databases()

    # show Tables
    mysql.tables()

    # Ping
    mysql.ping()

    # get connection cursor
    mysql.conn_cursor(cursorclass=None)

    # Close
    # crash process close
    mysql.close()

    # debug query : default True
    mysql.debug_query(False)
```

### MongoDB

---

```
    # show Database
    mongo.databases()

    # show Collections
    mongo.collections()

    # Ping
    mongo.ping()

    # SELECT
    mongo.select('COLLECTION_NAME','QUERY_STRING or DICTIONARY') -> pd.Dataframe

    # INSERT
    mongo.insert('COLLECTION_NAME','QUERY_STRING or DICTIONARY')
    mongo.insert_many('COLLECTION_NAME','QUERY_STRING or DICTIONARY')

    # UPDATE
    mongo.update('COLLECTION_NAME','FILTER_STRING or DICTIONARY', 'UPDATE_STRING or DICTIONARY')
    mongo.update_many('COLLECTION_NAME','FILTER_STRING or DICTIONARY', 'UPDATE_STRING or DICTIONARY')

    # DELETE
    mongo.delete('COLLECTION_NAME','QUERY_STRING or DICTIONARY')
    mongo.delete_many('COLLECTION_NAME','QUERY_STRING or DICTIONARY')

```

### ElasticSearch

---

```
    # CREATE
    elastic.index(index='INDEX_NAME')

    # DROP
    elastic.delete_index(index='INDEX_NAME')

    # SELECT
    elastic.search(body=query) -> any
    elastic.search_list(body=query, fetch_all=True) -> list
    elastic.search_dataframe(body=query, fetch_all=True) -> dataframe
    elastic.search_field(field='FIELD_NAME',value='VALUE') -> list

    # INSERT
    elastic.create(id='ID', body='JSON_BODY')

    #UPDATE
    elastic.update(id='ID', body='JSON_BODY')

    #DELETE
    elastic.delete(id='ID')

    # SCROLL
    elastic.prepare_scroll("farmers_index", query={"query": {"match_all": {}}}, source_filters=["name", "code"])
    chunk_list = elastic.next_scroll_chunk()

    # BULK 
    success, error_list = bulk_insert("farm_index", doc_list, id_field="farm_id")
    success, error_list = bulk_upsert("farm_index", doc_list, id_field="farm_id")
  
    # Ping
    elastic.ping()

    # Connection Information
    elastic.info()
```

### Code Quality

When creating new functions, please follow the Google style Python docstrings. See example below:

```
def example_function(param1: int, param2: str) -> bool:
    """Example function that does something.

    Args:
        param1: The first parameter.
        param2: The second parameter.

    Returns:
        The return value. True for success, False otherwise.

    """
```

## Version history

v0.1.0 initial version
v0.1.1 echoss_logger include
v0.1.7 mysql support query with params. return cursor.rowcount for insert/update/delete query
v1.0.0 mysql support query with list params
v1.0.1 elastic search_list fetch_all option, mongo support insert_many, delete_many, update_many method
v1.0.2 mysql reuse cursor
v1.0.7 echoss-query last version
v1.0.8 change package name to echoss-db
v1.0.11 update() check 'doc' or 'script' in body
