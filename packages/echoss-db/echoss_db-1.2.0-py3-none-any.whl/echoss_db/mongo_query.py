import json
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Any, List, Tuple, Union

from echoss_fileformat import FileUtil, get_logger, set_logger_level

logger = get_logger("echoss_query")


class MongoQuery:
    empty_dataframe = pd.DataFrame()
    empty_dict = {}

    def __init__(self, conn_info: str or dict):
        """
        Args:
            region_env(str) : Config File Regsion
            ex) conn_info = {
                                'mongo':
                                    {
                                        'host'  : int(ip),
                                        'port'  : int(port)),
                                        'db'    : str(db_name)
                                    }
                            }
        """
        if isinstance(conn_info, str):
            conn_info = FileUtil.dict_load(conn_info)
        elif not isinstance(conn_info, dict):
            raise TypeError("[Mongo] support type 'str' and 'dict'")
        required_keys = ['db']
        if (len(conn_info) > 0) and ('mongo' in conn_info) and all(key in conn_info['mongo'] for key in required_keys):
            if 'host' in conn_info['mongo'] and 'port' in conn_info['mongo']:
                self.client = MongoClient(
                    host=conn_info['mongo']['host'],
                    port=conn_info['mongo']['port']
                )
                self.db_name = conn_info['mongo']['db']
                self.db = self.client[self.db_name]
            elif 'uri' in conn_info['mongo']:
                self.client = MongoClient(
                    host=conn_info['mongo']['uri'],
                    directConnection=True
                )
                self.db_name = conn_info['mongo']['db']
                self.db = self.client[self.db_name]
            else:
                logger.debug(f"[Mongo] config info client connection keys (host, prot) or (url) not exist")
        else:
            logger.debug(f"[Mongo] config info not exist")

    def __str__(self):
        return f"MongoDB(client={self.client}, db_name={self.db_name})"

    @staticmethod
    def _parsing(*query: str):
        if len(query) != 1:
            default, modify = query
            return default, modify
        else:
            query = query[0]
            return query

    def _parse_query(self, query: Union[str, dict]) -> dict:
        """
        Parse a single query argument.

        Args:
            query (str or dict): Query to parse.

        Returns:
            dict: Parsed query dictionary.

        Raises:
            ValueError: If query string is invalid.
            TypeError: If query is neither string nor dict.
        """
        if isinstance(query, str):
            try:
                parsed = json.loads(query)
                if not isinstance(parsed, dict):
                    raise ValueError("Query string must represent a JSON object.")
                return parsed
            except json.JSONDecodeError as e:
                logger.error(f"Invalid query string: {query} - {e}")
                raise ValueError(f"Invalid query string: {query}") from e
        elif isinstance(query, dict):
            return query
        else:
            raise TypeError(f"Unsupported query type: {type(query)}. Must be str or dict.")

    def _parse_queries(self, *queries: Union[str, dict]) -> Union[dict, Tuple[dict, dict]]:
        """
        Parse multiple query arguments.

        Args:
            *queries (str or dict): Query arguments.

        Returns:
            Union[dict, Tuple[dict, dict]]:
                - Single query dict if one argument is provided.
                - Tuple of two query dicts (filter, update) if two arguments are provided.

        Raises:
            ValueError: If the number of queries is not 1 or 2.
        """
        if len(queries) == 1:
            return self._parse_query(queries[0])
        elif len(queries) == 2:
            return self._parse_query(queries[0]), self._parse_query(queries[1])
        else:
            raise ValueError("Invalid number of query arguments {len(queries)}. Expected 1 or 2.")

    def _parse_documents(self, documents: List[Union[str, dict]]) -> List[dict]:
        """
        Parse a list of documents for insert_many.

        Args:
            documents (List[str or dict]): List of documents to parse.

        Returns:
            List[dict]: List of parsed document dictionaries.

        Raises:
            ValueError: If any document string is invalid.
            TypeError: If any document is neither string nor dict.
        """
        parsed_docs = []
        for doc in documents:
            parsed_docs.append(self._parse_query(doc))
        return parsed_docs

    def _databse_exists(self, db_name: str) -> bool:
        try:
            return db_name in self.client.list_database_names()
        except PyMongoError as e:
            logger.error(f"[Mongo] list_database_names failed: {e}")
            return False

    def ping(self):
        """
        Args:
            Any

        Returns:
            str : DB Status
        """
        stat = self.client.admin.command('ping').keys()
        if 'ok' in str(stat):
            logger.debug(f"[Mongo] database connection success")
        else:
            raise ConnectionError('database connection fail')

    def databases(self):
        """
        Args:
            Any

        Returns:
            string : Database list
        """
        result = self.client.list_database_names()
        return pd.DataFrame(result, columns=['Database'])

    def collections(self, db_name: str = None) -> pd.DataFrame:
        """
        Args:
            db_name(str) : database name

        Returns:
            pd.DataFrame : collection dataframe
        """
        result = None
        if db_name is None or db_name == self.db_name:
            result = self.db.list_collection_names()
        else:
            if self._databse_exists(db_name):
                this_db = self.client[db_name]
                result = this_db.list_collection_names()
        if result is not None:
            return pd.DataFrame(result, columns=['Table'])
        else:
            return self.empty_dataframe

    def select(self, collection: str, query: Union[str, dict]) -> pd.DataFrame:
        """
        Args:
            collection(str) :
            query(Union[str, dict]) : Mongo select query string

        Returns:
            pd.DataFrame : DataFrame of query result
        """
        try:
            query_dict = self._parse_query(query)
            query_result = self.db[collection].find(query_dict)
            return pd.DataFrame(list(query_result))
        except Exception as e:
            logger.error(f"[Mongo] select failed. {e} ")
            return self.empty_dataframe

    def select_list(self, collection: str, query: Union[str, dict]) -> list:
        """
        Args:
            collection(str) :
            query(Union[str, dict]) : Mongo select query string

        Returns:
            list : list of dict
        """
        try:
            query_dict = self._parse_query(query)
            query_result = self.db[collection].find(query_dict)
            return list(query_result)
        except Exception as e:
            logger.error(f"[Mongo] select failed. {e} ")
            return []

    def select_one(self, collection: str, query: Union[str, dict]) -> dict:
        """
        Args:
            collection(str) :
            query(Union[str, dict]) : Mongo select query string

        Returns:
            list : list of dict
        """
        try:
            query_dict = self._parse_query(query)
            query_result = self.db[collection].find_one(query_dict)
            return dict(query_result)
        except Exception as e:
            logger.error(f"[Mongo] select failed. {e} ")
            return self.empty_dict

    def insert(self, collection: str, document: Union[str, dict]) -> None:
        """
        Args:
            collection(str) : target collection
            document(Union[str, dict]) : Mongo insert query string

        Returns:
        """
        try:
            query_dict = self._parse_query(document)
            insert_result = self.db[collection].insert_one(query_dict)
            logger.debug(f"[Mongo] insert {insert_result} success.")
        except Exception as e:
            logger.error(f"[Mongo] insert failed. {e} ")

    def insert_many(self, collection: str, documents: list) -> None:
        """
        Args:
            collection(str) : target collection
            query(Union[str, dict]) : Mongo insert query string

        Returns:
        """
        query_dict = self._parse_documents(documents)
        try:
            insert_result = self.db[collection].insert_many(query_dict)
            logger.debug(f"[Mongo] insert_many {insert_result} success.")
        except PyMongoError as e:
            logger.error(f"[Mongo] insert_many failed. {e} ")

    def update(self, collection: str, filter_query: Union[str, dict], update_query: Union[str, dict]) -> None:
        """
        Args:
            collection(str) : target collection
            filter_query(str or dict) : filter query
            update_query(str or dict) : update operation

        Returns:
        """
        filter_dict, update_dict = self._parse_queries(filter_query, update_query)
        if not (filter_dict is None or update_dict is None):
            try:
                update_result = self.db[collection].update_one(filter_dict, update_dict)
                logger.debug("[Mongo] update_one {update_result} success.")
            except PyMongoError as e:
                logger.error(f"[Mongo] insert_many failed. {e} ")

    def update_many(self, collection: str, filter_query: Union[str, dict], update_query: Union[str, dict]) -> None:
        """
        Update multiple documents in the specified collection.

        Args:
            collection (str): Target collection name.
            filter_query (str or dict): Query to filter documents to update.
            update_query (str or dict): Update operations to apply.

        Returns:
        """
        filter_dict, update_dict = self._parse_queries(filter_query, update_query)
        if not (filter_dict is None or update_dict is None):
            try:
                result = self.db[collection].update_many(filter_dict, update_dict)
                logger.debug(f"[Mongo] Updated {result.modified_count} document(s) in '{collection}' collection.")
            except PyMongoError as e:
                logger.error(f"[Mongo] Error updating documents in '{collection}' collection: {e}")

    def delete(self, collection: str, query: str or dict) -> None:
        """
        Args:
            collection(str) : target collection
            query(str or dict) : Mongo delete query string

        Returns:
        """
        query_dict = self._parse_query(query)
        if not query_dict:
            raise ValueError("can't delete all collection")
        else:
            try:
                result =  self.db[collection].delete_one(query_dict)
                logger.debug(f"[Mongo] delete_one {result} success.")
            except PyMongoError as e:
                logger.error(f"[Mongo] delete_one failed.: {e}")

    def delete_many(self, collection: str, query: str or dict) -> None:
        """
        Args:
            collection(str) : target collection
            query(str or dict) : Mongo delete query string

        Returns:
        """
        query_dict = self._parse_query(query)
        if not query_dict:
            raise ValueError("can't delete all collection")
        else:
            try:
                result =  self.db[collection].delete_many(query_dict)
                logger.debug(f"[Mongo] delete {result.deleted_count} document(s) success.")
            except PyMongoError as e:
                logger.error(f"[Mongo] delete_many failed.: {e}")

    def new_index(self, collection: str, document: str) -> int:
        """
        Args:
            collection(str) : target collection
            document(str) : target document
        Returns:
            int() : maximum value
        """
        sort_list = [
            (f"{document}", -1)
        ]
        max_rows_old = list(eval(f"self.db.{collection}.find().sort([('{document}',-1)]).limit(1)"))
        max_rows = list(self.db[collection].find().sort(sort_list).limit(1))
        if len(max_rows) > 0:
            max_value = max_rows[0][document]
            index = max_value + 1
        else:
            index = 1

        return index

