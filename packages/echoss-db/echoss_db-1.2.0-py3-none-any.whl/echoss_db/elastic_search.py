import pandas as pd
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk as helpers_bulk
from opensearchpy.exceptions import NotFoundError
from typing import Any, List, Tuple, Dict, Optional, Union

from echoss_fileformat import FileUtil, get_logger, set_logger_level

logger = get_logger("echoss_query")


class ElasticSearch:
    conn = None
    query_match_all = {"query": {"match_all": {}}}
    empty_dataframe = pd.DataFrame()
    query_cache = False
    default_size = 1000

    def __init__(self, conn_info: str or dict):
        """
        Args:
            conn_info : configration dictionary (index is option)
            ex) conn_info = {
                                'elastic':
                                    {
                                        'user'  : str(user),
                                        'passwd': str(passwd),
                                        'host'  : str(host),
                                        'port' : int(port),
                                        'scheme' : http or https
                                    }
                            }

        """
        if isinstance(conn_info, str):
            conn_info = FileUtil.dict_load(conn_info)
        elif not isinstance(conn_info, dict):
            raise TypeError("ElasticSearch support type 'str' and 'dict'")

        required_keys = ['host', 'port']
        if (len(conn_info) > 0) and ('elastic' in conn_info) and (conn_info['elastic'] for k in required_keys):
            es_config = conn_info['elastic']
        else:
            raise TypeError("[Elastic] config info not exist")

        self.user = es_config.get('user')
        self.passwd = es_config.get('passwd')
        self.auth = (self.user, self.passwd) if self.user and self.passwd else None

        self.host = es_config['host']
        self.port = es_config['port']
        self.scheme = es_config.get('scheme', 'https')
        if 'https' == self.scheme:
            self.use_ssl = True
            self.verify_certs = es_config.get('verify_certs', True)
        else:
            self.use_ssl = False
            self.verify_certs = False

        self.index_name = es_config.get('index')

        self.hosts = [{
            'host': self.host,
            'port': self.port
        }]

        self.http_compress = es_config.get('http_compress', False)

        # Retrieve timeout from config or set a default
        # This is the timeout for establishing and reading from the connection
        self.connection_timeout = es_config.get('timeout', 30)  # Default to 30 seconds if not provided in config

        # re-use connection
        self.conn = self._connect_es()

        # extra config
        if 'default_size' in es_config:
            self.default_size = es_config['default_size']

        # scroll context
        self._scroll_id = None
        self._scroll_context_ttl = es_config.get('scroll_context_ttl','2m')
        self._scroll_query = None
        self._scroll_size = es_config.get('scroll_size', 10000)
        self._scroll_source_fields = None
        self._scroll_index = self.index_name

    def __str__(self):
        return f"ElasticSearch(hosts={self.hosts}, index={self.index_name})"

    def _connect_es(self):
        """
        ElasticSearch Cloud에 접속하는 함수
        """
        try:
            es_conn = OpenSearch(
                hosts=self.hosts,
                http_auth=self.auth,
                scheme=self.scheme,
                http_compress=self.http_compress,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                ssl_assert_hostname=False,
                ssl_show_warn=False,
                timeout=self.connection_timeout,  # <--- THIS IS THE KEY LOCATION
                max_retries=5,  # <--- Optional: Add retries
                retry_on_timeout=True  # <--- Optional: Specifically retr
            )
            if es_conn is None or es_conn.ping() is False:
                raise ValueError(f"open elasticsearch is failed or health ping failed.")
            return es_conn
        except Exception as e:
            raise ValueError("Connection failed by config. Please check config data")

    def _clear_scroll_context(self):
        """내부 스크롤 컨텍스트를 정리합니다."""
        if self._scroll_id:
            try:
                self.conn.clear_scroll(scroll_id=self._scroll_id)
                logger.debug(f"Scroll context {self._scroll_id} cleared.")
            except NotFoundError:
                logger.error(f"Scroll context {self._scroll_id} already expired or not found.")
            except Exception as e:
                logger.error(f"Error clearing scroll context {self._scroll_id}: {e}", exc_info=True)
            finally:
                self._scroll_id = None
                self._scroll_query = None
                self._scroll_size = 10000
                self._scroll_source_fields = None
                self._scroll_index = self.index_name

    def prepare_scroll(self, index_name: str,  query: dict = None, size: int = 10000,
                       source_fields: Union[List[str],bool] = True, scroll_ttl: str = "2m"):
        """
        스크롤 조회를 위한 초기 설정을 준비합니다.
        새로운 스크롤을 시작하기 전에 반드시 호출해야 합니다.

        Args:
            index_name: 조회할 Elasticsearch 인덱스 이름.
            query: Elasticsearch 쿼리 본문 (기본값: match_all).
            size: 한 번에 가져올 문서의 수 (청크 크기), 기본값 10000
            source_fields: 가져올 _source 필드 목록
                - List[str]: 특정 필드만 포함합니다 (예: ['field1', 'field2']).
                - True: 모든 _source 필드를 포함합니다.
                - False: _source 필드를 완전히 제외합니다.
            scroll_ttl: 스크롤 컨텍스트 유지 시간 (예: "2m", "10s"), 기본값 "2m".
        """
        self._clear_scroll_context()  # 이전 스크롤 컨텍스트 정리
        self._scroll_index = index_name
        self._scroll_query = query if query else {"match_all": {}}
        self._scroll_size = size
        self._scroll_source_fields = source_fields
        self._scroll_context_ttl = scroll_ttl
        logger.debug(
            f"Scroll prepared for '{index_name}' with query: {self._scroll_query}, size: {self._scroll_size}, TTL: {self._scroll_context_ttl}"
        )

    def next_scroll_chunk(self) -> list:
        """
        준비된 스크롤에서 다음 문서 청크를 가져옵니다.
        첫 호출 시에는 초기 검색을, 이후 호출 시에는 스크롤 ID를 사용하여 데이터를 가져옵니다.
        더 이상 문서가 없거나 에러 발생 시 빈 리스트를 반환하고 컨텍스트를 정리합니다.

        :return: 문서 _source (dict) 리스트. 더 이상 문서가 없으면 빈 리스트.
        """
        response = None
        try:
            if self._scroll_index is None:
                logger.error("Scroll not prepared. Call prepare_scroll() before next_scroll_chunk().")
                return []

            if self._scroll_id is None:
                # 첫 번째 호출: 초기 검색 수행
                search_body = {
                    "query": self._scroll_query,
                    "_source": self._scroll_source_fields
                }
                response = self.conn.search(
                    index=self._scroll_index,
                    scroll=self._scroll_context_ttl,
                    size=self._scroll_size,
                    body=search_body
                )
                self._scroll_id = response['_scroll_id']
                logger.debug(f"Initial scroll chunk fetched. Scroll ID: {self._scroll_id}")
            else:
                # 후속 호출: scroll ID 사용
                response = self.conn.scroll(
                    scroll_id=self._scroll_id,
                    scroll=self._scroll_context_ttl
                )
                self._scroll_id = response['_scroll_id']  # scroll_id 업데이트

            doc_list = response.get('hits', {}).get('hits', [])
            if not doc_list:
                logger.debug("No more data in scroll.")
                self._clear_scroll_context()  # 모든 데이터 조회 완료 후 컨텍스트 정리
            return doc_list
        except NotFoundError:
            logger.warning(f"Scroll context {self._scroll_id} not found or expired. Clearing context.")
            self._clear_scroll_context()
            return []
        except Exception as e:
            logger.error(f"An error occurred during scroll operation: {e}", exc_info=True)
            self._clear_scroll_context()  # 에러 발생 시 컨텍스트 정리
            return []

    def _bulk_operations(self, actions: list, chunk_size: int = 500, raise_on_error: bool = True,
                        max_retries: int = 3, request_timeout: int = 120) -> tuple[int, list]:
        """
        주어진 액션(문서) 리스트를 특정 인덱스에 벌크로 실행합니다.
        성공/실패 결과를 반환하며, 로깅을 포함합니다.

        Args:
            actions (list): Elasticsearch _bulk API에 전달할 action 리스트.
                        각 action dict는 반드시 '_index' 필드를 포함해야 합니다.
                        예: {"_index": "idx_name", "_id": "id1", "_source": {...}, "_op_type": "index"}
                        update or insert 예: { "_op_type": "update", "_index": farmers_es.index_name, "_id": rsbsa_no, "doc": farmer_doc,  "doc_as_upsert": True}
            chunk_size (int): 한 번에 전송할 문서의 개수.
            raise_on_error (bool): 개별 문서 오류 발생 시 예외를 발생시킬지 여부. False이면 오류가 발생해도 계속 진행하며 오류 리스트를 반환.
            max_retries (int): 네트워크/클라이언트 오류 발생 시 전체 요청에 대한 최대 재시도 횟수.
            request_timeout (int): 요청에 대한 응답 대기 시간(초)

        :return: (성공한 작업 수, 실패한 작업 리스트)
        """
        if not actions:
            logger.info("No actions provided for bulk operation.")
            return 0, []

        success_count = 0
        error_items = []
        operation_kinds = ['index', 'update', 'delete', 'create']

        try:
            # helpers.bulk는 이터레이터를 받아서 처리하므로, actions 리스트를 직접 전달
            # raise_on_error=False로 설정하여 helpers.bulk가 내부적으로 예외를 발생시키지 않도록 하고
            # 우리가 직접 오류를 처리하거나 로깅합니다.
            success, errors = helpers_bulk(
                self.conn,
                actions,
                chunk_size=chunk_size,
                raise_on_exception=raise_on_error,
                raise_on_error=raise_on_error,  # 개별 문서 오류 시 예외 발생 방지
                max_retries=max_retries,
                request_timeout=request_timeout
            )

            success_count = success
            error_items = errors
            total_size = success + len(errors)

            if success > 0:
                logger.debug(f"Bulk operation : {success} documents processed successfully.")
            if errors:
                logger.warning(f"Bulk operation : {len(errors)} documents failed.")
                for i, err_item in enumerate(errors):
                    # errors는 [{'index': {'_index': '...', 'status': 400, 'error': {...}, 'data': {...}}}] 형태
                    for op in operation_kinds:
                        if op in err_item:
                            doc_id = err_item[op].get('_id', 'N/A')
                            error_type = err_item[op].get('error', {}).get('type', 'UnknownError')
                            error_reason = err_item[op].get('error', {}).get('reason', 'No reason')
                            error_caused_by = err_item[op].get('error', {}).get('caused_by', 'No caused_by')
                            logger.error(f"  Failed bulk {op} item {i}/{total_size} _id: {doc_id} Error type={error_type}, reason='{error_reason}, caused_by='{error_caused_by}'")
                            break

                if raise_on_error:
                    raise Exception(f"Bulk operation completed with {len(errors)} errors. Check logs for details.")

        except Exception as e:
            logger.error(f"An unexpected error occurred during bulk operation {e}", exc_info=True)
            if raise_on_error:
                raise

        return success_count, error_items

    def bulk_insert(self, index_name: str, doc_list: List[Dict], id_field: Optional[str] = None, raise_on_error: bool = True):
        """벌크 문서 생성
        Args:
            index_name: 대상 index name
            doc_list: 문서 목록
            id_field: 문서에서 id 필드로 사용할 필드, None  이면 자동 _id 사용
            raise_on_error: 개별 문서 오류 발생 시 예외를 발생시킬지 여부

        Returns:
            (성공한 작업 수, 실패한 작업 리스트)
        """
        actions = []
        for doc in doc_list:
            action = {  "_op_type": "index", "_index" : index_name, "_source": doc}
            if  id_field and id_field in doc:
                action["_id"] = doc[id_field]
            actions.append(action)

        return self._bulk_operations(actions, raise_on_error=raise_on_error)

    def bulk_upsert(self, index_name:str, doc_list: List[Dict], id_field: Optional[str],
                    id_list: Optional[list] = None, raise_on_error: bool = True):
        """벌크 문서 업데이트 id 에 해당하는 문서가 없으면 생성
        Args:
            index_name: 대상 index name
            doc_list: 문서 목록
            id_field: 문서에서 id 필드로 사용할 필드
            id_list (list): id_field 가 None 일 때에 doc_list 와 같은 길이의 id 목록 사용
            raise_on_error: 개별 문서 오류 발생 시 예외를 발생시킬지 여부

        Returns:
            (성공한 작업 수, 실패한 작업 리스트)
        """
        if id_field is None:
            if id_list is None or len(id_list) == 0:
                logger.error(f"id_field or id_list must be set")
                return 0, []

            if len(doc_list) != len(id_list):
                logger.error(f"{len(doc_list)=} vs. {len(id_list)=}")
                return 0, []

        actions = []
        for i, doc in enumerate(doc_list):
            action = {"_op_type": "update", "_index": index_name, "doc": doc, "doc_as_upsert": True}
            if id_field:
                if id_field in doc:
                    action["_id"] = doc[id_field]
            elif id_list is not None:
                action['_id'] = id_list[i]
            actions.append(action)

        return self._bulk_operations(actions, raise_on_error=raise_on_error)

    def ping(self) -> bool:
        """
        Elastic Search에 Ping
        """
        if self.conn:
            return self.conn.ping()
        else:
            return False

    def info(self) -> dict:
        """
        Elastic Search Information
        """
        return self.conn.info()

    def exists(self, id: str or int, index=None) -> bool:
        """
        Args:
            id(str) : 확인 대상 document id
            index(str) : 확인 대상 index when None self.index_name
        Returns:
            boolean
        """
        if index is None:
            index = self.index_name
        return self.conn.exists(index, id)

    def search(self, body: dict = None, index=None) -> dict:
        """
        Args:
            index(str) : 대상 index
            body(dict) : search body
        Returns:
            search result
        """
        if index is None:
            index = self.index_name
        if body is None:
            body = self.query_match_all

        response = self.conn.search(
            index=index,
            body=body
        )
        return response

    def to_dataframe(self, es_result) -> pd.DataFrame:
        """
        Elasticsearch 검색 결과에서 DataFrame을 생성합니다.
        다음 세 가지 입력 유형을 처리합니다:
        1. 전체 Elasticsearch 응답 (dict 형태)
        2. '_id'와 '_source'를 포함하는 문서들의 리스트 (hits.hits 부분)
        3. '_source' 필드 값들만 추출된 리스트

        Args:
            es_result (dict or list): Elasticsearch 검색 결과.

        Returns:
            pd.DataFrame: 생성된 DataFrame. 유효한 결과가 없으면 빈 DataFrame을 반환합니다.
        """
        doc_list = []
        if isinstance(es_result, dict) and 'hits' in es_result and 'hits' in es_result['hits']:
            doc_list = es_result['hits']['hits']
        elif isinstance(es_result, list) and len(es_result) > 0 and isinstance(es_result[0], dict):
            # '_id' 또는 '_source'를 포함하는 문서들의 리스트인 경우 (나머지 리스트 형태)
            if '_id' not in es_result[0]:
                # 3. '_source' 필드 값들만 추출된 리스트인 경우
                return pd.DataFrame(es_result)
            else:
                doc_list = es_result

        if not doc_list:
            return self.empty_dataframe

        # '_id' 와 '_source' 로 DataFrame 생성
        has_id = '_id' in doc_list[0]
        has_source ='_source' in doc_list[0]
        if has_id and has_source:
            # _id와 _source 모두 있는 경우
            data = [doc['_source'] for doc in doc_list]
            index = [doc['_id'] for doc in doc_list]
            df = pd.DataFrame(data, index=index)
            return df
        elif has_id and not has_source:
            # _id만 있고 _source가 없는 경우 (예: _source: False 쿼리)
            # 인덱스만 있고 데이터 컬럼이 없는 DataFrame 생성
            index = [doc['_id'] for doc in doc_list]
            df = pd.DataFrame(index=index)
            return df
        else:
            # 비정상 doc_list
            return self.empty_dataframe

    def _fetch_all_hits(self, index: str, body: dict) -> List[dict]:
        """
        Scroll API를 사용하여 모든 검색 결과를 가져옵니다.

        Args:
            index (str): 대상 인덱스 이름
            body (dict): 검색 쿼리
        Returns:
            all_hits (list): 모든 검색 결과 리스트
        """
        all_hits = []
        scroll_time = '2m'  # Scroll context 유지 시간

        # 'size' 값 확인 및 설정
        size = body.get('size', 1000)
        body = body.copy()  # 원본 body를 변경하지 않도록 복사
        body['size'] = size
        scroll_id = None
        try:
            # 초기 검색 요청
            response = self.conn.search(
                index=index,
                body=body,
                scroll=scroll_time
            )

            scroll_id = response['_scroll_id']
            hits = response['hits']['hits']
            all_hits.extend(hits)

            # 더 이상 결과가 없을 때까지 반복
            while len(hits) > 0:
                response = self.conn.scroll(
                    scroll_id=scroll_id,
                    scroll=scroll_time
                )
                scroll_id = response['_scroll_id']
                hits = response['hits']['hits']
                all_hits.extend(hits)

            # Scroll context 삭제
            self.conn.clear_scroll(scroll_id=scroll_id)

        except Exception as e:
            logger.error(f"Error fetching all hits: {e}")
            # Scroll context 정리 시도
            try:
                if scroll_id is not None:
                    self.conn.clear_scroll(scroll_id=scroll_id)
            except Exception as ce:
                logger.error(f"connection clear_scroll failed : {ce}")
            raise

        return all_hits

    def search_list(self, body: dict = None, index=None, fetch_all: bool = True) -> List[dict]:
        """
        Args:
            body(dict) : search body
            index(str) : 대상 index
            fetch_all(bool) : fetch all hits
        Returns:
            result(list) : search result of response['hits']['hits']
        """
        if index is None:
            index = self.index_name
        if body is None:
            body = self.query_match_all
        if fetch_all and 'size' not in body:
            return self._fetch_all_hits(index, body)
        else:
            response = self.conn.search(
                index=index,
                body=body
            )
            if len(response) > 0 and 'hits' in response and 'hits' in response['hits']:
                return response['hits']['hits']
        return []

    def search_dataframe(self, body: dict = None, index=None, fetch_all: bool = True) -> pd.DataFrame:
        hits_list = self.search_list(body=body, index=index, fetch_all=fetch_all)
        return self.to_dataframe(hits_list)

    def search_field(self, field: str, value: str, index=None, fetch_all:bool=True) -> list:
        """
        해당 index, field, value 값과 비슷한 값들을 검색해주는 함수 \n
        Args:
            field(str) : 검색 대상 field
            value(str) : 검색 대상 value
            index(str) : 대상 index if not self.index_name
            fetch_all(bool) : fetch all document when True else fetch by size

        Returns:
            result(list) : 검색 결과 리스트
        """
        if index is None:
            index = self.index_name

        query_body = {
                'query': {
                    'match': {field: value}
                }
            }
        if fetch_all:
            return self._fetch_all_hits(index, query_body)
        else:
            response = self.conn.search(
                index=index,
                body=query_body
            )
            return response['hits']['hits']

    def get(self, doc_id: str or int, index=None) -> dict:
        """
        index에서 id와 일치하는 데이터를 불러오는 함수
        Args:
            doc_id(str) : 가져올 대상 id
            index(str) : 대상 index if not self.index_name

        Returns:
            결과 데이터 (dict)

        """
        if index is None:
            index = self.index_name
        return self.conn.get(index=index, id=doc_id)

    def get_source(self, id: str or int, index=None) -> dict:
        """
        index에서 id와 일치하는 데이터의 소스만 불러오는 함수 \n
        Args:
            id(str) : 가져올 대상 id \n
        Returns:
            result(dict) : 결과 데이터

        """
        if index is None:
            index = self.index_name
        return self.conn.get_source(index, id)

    def index(self, index: str, body: dict, id: str or int = None) -> Any:
        """
        index를 생성하고 해당 id로 새로운 document를 생성하는 함수 \n
        (index를 추가하고 그 내부 document까지 추가하는 방식) \n
        Args:
            index(str) : 생성할 index name
            body(dict) : 입력할 json 내용
            id(str) : 생성할 document id
        Returns:
            생성 결과
        """
        return self.conn.index(index, body, id=id)

    def update(self, id: str or int, body: dict, index=None) -> Any:
        """
        기존 데이터를 id를 기준으로 body 값으로 수정하는 함수 \n
        Args:
            id(str) : 수정할 대상 id \n
            body(dict) : data dict to update
            index(str) : 생성할 index name \n
        Returns:
            처리 결과
        """
        if index is None:
            index = self.index_name

        if 'script' in body or 'doc' in body:
            doc_body = body
        else:
            doc_body = {
                'doc' : body
            }
        return self.conn.update(index, id, doc_body)

    def delete(self, id: str or int, index=None) -> Any:
        """
        삭제하고 싶은 데이터를 id 기준으로 삭제하는 함수 \n
        Args:
            id(str) : 삭제 대상 id \n
            index(str) : 생성할 index name \n
        Returns:
            result : 처리 결과
        """
        if index is None:
            index = self.index_name
        return self.conn.delete(index, id)

    def delete_index(self, index):
        """
        인덱스를 삭제하는 명령어 신중하게 사용해야한다.\n
        Args:
            index(str) : 삭제할 index
        Returns:
            result(str) : 처리 결과
        """
        return self.conn.indices.delete(index)


    def bulk(self, actions:list, index=None) -> Tuple[int, int]:
        """

        Args:
            actions: bulk action list
            index: 대상 index name

        Returns:
            success, failed
        """
        if index is None:
            index = self.index_name

        if actions:
            success, failed = helpers_bulk(self.conn, actions, raise_on_error=False)
            logger.debug(f"[Bulk] Success: {success}, Failed: {failed}")
            return success, failed
        else:
            return 0, len(actions)

    def close(self):
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
        except AttributeError:
            pass

    def __del__(self):
        self.close()

