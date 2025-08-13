from __future__ import annotations
from datetime import datetime
from functools import wraps
import pandas as pd
import time
from typing import Any, Iterable, List, Optional, Tuple, Union

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection, Result 
from sqlalchemy.exc import SQLAlchemyError, DBAPIError

from echoss_fileformat import FileUtil, get_logger

logger = get_logger("echoss_db")

# --------------------------------------------------------------------------------------
# 공통 Decorator 
# --------------------------------------------------------------------------------------
def log_execution_time(func):
    """Decorator to log the execution time of a method when use_query_debug is True."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, 'use_query_debug', False):
            # If use_query_debug is False, just call the function without logging
            return func(self, *args, **kwargs)

        # Start timing
        start_time = time.time()
        try:
            # Execute the original function
            result = func(self, *args, **kwargs)
            return result
        finally:
            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time  # Seconds
            # Log elapsed time in seconds with three decimal places
            logger.debug(f"{func.__name__}() executed in {elapsed_time:.3f} seconds")
    return wrapper


def _safe_log_param(p):
    return '<binary>' if isinstance(p, (bytes, bytearray)) else repr(p)


def parse_query(keyword):
    """Decorator to parse the query, check for the keyword and generate result query_str with params"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, query_str: str, params=None, *args, **kwargs):
            # Check if the query contains the specified keyword
            if keyword not in query_str.upper():
                raise ValueError(f'Input query does not include "{keyword}"')

            # 불필요한 세미콜론 제거 (trailing only) 끝의 세미콜론/공백만 안전하게 제거 (SQLAlchemy는 ; 불필요)
            # 예: "SELECT ... ;   " -> "SELECT ..."
            # Parse the query: append semicolon if not present
            query_str = query_str.strip().rstrip(";").rstrip()

            # Log the final query when use_query_debug is True
            if getattr(self, 'use_query_debug', False):
                if params and isinstance(params, list):
                    rows = len(params)
                    if rows > 0:
                        first_param = params[0]
                        if isinstance(first_param, (list, tuple)):
                            safe_example = [_safe_log_param(p) for p in first_param]
                        elif isinstance(first_param, dict):
                            safe_example = {k: _safe_log_param(v) for k, v in first_param.items()}
                        else:
                            safe_example = first_param
                        logger.debug(f'mysql_query.{func.__name__}() bulk example """{query_str}""" with {safe_example} for {rows} rows')
                    else:
                        logger.warning(f'mysql_query.{func.__name__}() bulk query """{query_str}""" with empty params')
                else:
                    if isinstance(params, tuple):
                        safe_example = [_safe_log_param(p) for p in params]
                    elif isinstance(params, dict):
                        safe_example = {k: _safe_log_param(v) for k, v in params.items()}
                    else:
                        safe_example = params
                    logger.debug(f'mysql_query.{func.__name__}() parsed """{query_str}""" with {safe_example}')

            # Call the original function with the parsed query
            return func(self, query_str, params, *args, **kwargs)
        return wrapper
    return decorator


# ##################################################################################################
# Main Classes and Functions
# ##################################################################################################


class MysqlQuery:
    """
    기존 PyMySQL 기반 래퍼를 SQLAlchemy 2.x 기반으로 재구현.
    - 엔진 풀/세션 관리
    - exec_driver_sql 로 DBAPI 파라미터(%s) 호환
    - sqlalchemy 방식인 :name 태그 방식으로 할 경우에는 use_percent_param = False  로 설정
    - 메서드/반환 타입 호환 유지
    """
    engine: Optional[Engine] = None
    empty_dataframe = pd.DataFrame()
    use_query_debug: bool = True
    use_percent_param: bool = True

    def __init__(self, conn_info: Union[str, dict], compress=False, 
                 pool_size:int = 5, pool_timeout: int = 30, pool_recycle: Optional[int] = None,
                 use_percent_param: bool = True):
        """
        Args:
            conn_info : configration dictionary
                (ex) conn_info = {
                                'mysql':
                                    {
                                        'user'  : str(user),
                                        'passwd': str(pw),
                                        'host'  : str(ip),
                                        'port'  : int(port)
                                        'db'    : str(db_name),
                                        'charset': str(utf8)
                                    }
                            }
            compress: 미사용(호환 유지용 파라미터)
            pool_size: 기본 연결 풀 크기
            pool_timeout: 연결 대기 시간 (초)
            pool_recycle: 연결 재사용 시간 (초), None이면 pool_timeout * 60으로 자동 계산
            use_percent_param:  use %s param style, if false sqlalchemy :name tag style query param
        """
        if isinstance(conn_info, str):
            conn_info = FileUtil.dict_load(conn_info)
        elif not isinstance(conn_info, dict):
            raise TypeError("MysqlQuery support type 'str' and 'dict'")
        
        self.pool_size = pool_size
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle if pool_recycle is not None else pool_timeout * 60
        self.use_percent_param = use_percent_param
        
        required_keys = ['user', 'passwd', 'host', 'db']
        if (len(conn_info) > 0) and ('mysql' in conn_info) and all(key in conn_info['mysql'] for key in required_keys):
            m = conn_info["mysql"]
            self.user = m['user']
            self.passwd = m['passwd']
            self.host = m['host']
            self.port = m.get('port', 3306)
            self.db = m['db']
            self.charset = m.get('charset', 'utf8mb4')
        else:
            logger.error(f'[MySQL] config info not exist or any required keys are missing {required_keys}')
            raise ValueError("invalid conn_info")
        
        self._connect_db()

    def __str__(self):
        if self.engine:
            return f"Mysql connected(host={self.host}, port={self.port}, db={self.db})"
        else:
            return f"Mysql disconnected host={self.host}, port={self.port}, db={self.db})"

    def query_debug(self, use_query_debug=False):
        if isinstance(use_query_debug, bool):
            self.use_query_debug = use_query_debug
        logger.debug(f"use_query_debug = {self.use_query_debug}")

    def ping(self) -> bool:
        try:
            with self.engine.connect() as conn:
                rs = self._execute_query(conn, "SELECT 1")
                status = f"[MySQL] database {self.__str__()} connection success"
                logger.debug(status)
                return True
        except SQLAlchemyError as e:
            status = f"database {self.__str__()} connection fail: {e}"
            logger.error(status)
        return False

    def _connect_db(self):
        # SQLAlchemy MySQL URL (PyMySQL)
        # URL 구성 시 특수문자 이스케이핑 처리
        from urllib.parse import quote_plus
        escaped_passwd = quote_plus(str(self.passwd))
        
        url = f"mysql+pymysql://{self.user}:{escaped_passwd}@{self.host}:{self.port}/{self.db}"
        try:
            self.engine = create_engine(
                url,
                echo=False,
                pool_size=self.pool_size,
                max_overflow=self.pool_size * 2,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=True,
                connect_args={
                    "charset": self.charset,
                    "autocommit": False
                } 
            )
            logger.info(f"[MySQL] DB connected.")
        except SQLAlchemyError as e:
            logger.error(f"[MySQL] DB connection failed. {self.__str__()} : {e}")
            raise

    @log_execution_time
    def _execute_query(self, conn: Connection, query_str: str, params=None) -> Result[Any]:
        """Wraps execute and logs execution time."""
        if self.use_percent_param:
            if params is None or isinstance(params, (list, tuple)):
                return conn.exec_driver_sql(query_str, params)
            else:
                # 단일 값 → tuple 변환
                return conn.exec_driver_sql(query_str, (params,))
        else:
            # :name 스타일 (SQLAlchemy text 객체 방식)
            if params is not None and not isinstance(params, dict):
                raise TypeError("When use_percent_param=False, params must be a dict for :name binding.")
            return conn.execute(text(query_str), parameters=params)

    # @log_execution_time
    # def _execute_many(self, conn, query_str, params=None):
    #     """Wraps cur.execute() and logs execution time."""
    #     return conn.exec_driver_sql(query_str, params)

    @log_execution_time
    def _fetch_one(self, rs:Result):
        """Wraps cur.fetchone() and logs execution time."""
        return rs.fetchone()

    @log_execution_time
    def _fetch_all(self, rs:Result):
        """Wraps cur.fetchone() and logs execution time."""
        return rs.fetchall()

    @log_execution_time
    def _fetch_many(self, rs:Result, fetch_size):
        """Wraps cur.fetchone() and logs execution time."""
        return rs.fetchmany(size=fetch_size)

    def databases(self) -> pd.DataFrame:
        """
        Args:
        Returns:
            pd.DataFrame() : database dataframe
        """
        try:
            with self.engine.connect() as conn:
                # conn.exec_driver_sql 대신 pandas.read_sql을 사용하면 훨씬 간결합니다.
                return pd.read_sql('SHOW DATABASES', conn)
        except SQLAlchemyError as e:
            logger.error(f"[MySQL] databases Exception: {e}")
            return self.empty_dataframe

    def tables(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame() : table dataframe
        """
        try:
            with self.engine.connect() as conn:
                return pd.read_sql('SHOW TABLES', conn)
        except SQLAlchemyError as e:
            logger.error(f"[MySQL] tables Exception: {e}")
            return self.empty_dataframe
        
    # ##################################3###
    #  Table method
    # ######################################
    @parse_query('CREATE')
    def create(self, query_str: str, params=None) -> None:
        """
        Args:
            query_str(str) : MySQL create query string
            params: query parameters like % operator
        """
        try:
            with self.engine.begin() as conn:
                self._execute_query(conn, query_str, params)
        except SQLAlchemyError  as e:
            logger.debug(f"[MySQL] Create Exception : {e}")

    @parse_query('DROP')
    def drop(self, query_str: str, params=None) -> None:
        """
        Args:
            query_str(str) : MySQL drop query string
            params: query parameters like % operator
        """
        try:
            with self.engine.begin() as conn:
                self._execute_query(conn, query_str, params)
        except SQLAlchemyError  as e:
            logger.debug(f"[MySQL] Drop Exception : {e}")

    @parse_query('TRUNCATE')
    def truncate(self, query_str: str, params=None) -> None:
        """
        Args:
            query_str(str) : MySQL truncate query string
            params: query parameters like % operator
        """
        try:
            with self.engine.begin() as conn:
                self._execute_query(conn, query_str, params)
        except SQLAlchemyError  as e:
            logger.debug(f"[MySQL] Truncate Exception : {e}")

    @parse_query('ALTER')
    def alter(self, query_str: str, params=None) -> None:
        """
        Args:
            query_str(str) : MySQL alter query string
            params: query parameters like % operator
        """
        try:
            with self.engine.begin() as conn:
                self._execute_query(conn, query_str, params)
        except SQLAlchemyError  as e:
            logger.debug(f"[MySQL] Alter Exception : {e}")

    # ##################################3###
    #  Quqery method
    # ######################################
    @parse_query('SELECT')
    def select_one(self, query_str: str, params=None) -> dict:
        """
        Args:
            query_str(str): MySQL select query string that returns a single row
            params: query string format parameters like % style
        Returns:
            dict: A single dictionary result from the query
        """
        try:
            with self.engine.connect() as conn:
                rs = self._execute_query(conn, query_str, params)
                row = self._fetch_one(rs)
                if row:
                    return row
                else:
                    logger.debug("[MySQL] No data found")
                    return {}
        except SQLAlchemyError  as e:
            logger.debug(f"[MySQL] SELECT Exception: {e}")
            return {}

    @parse_query('SELECT')
    def select_list(self, query_str: str, params=None) -> list:
        """
        Args:
            query_str(str) : MySQL select query string
            params: query string format parameters like % style
        Returns:
            list() : List of query result
        """
        try:
            with self.engine.connect() as conn:
                rs = self._execute_query(conn, query_str, params)
                rows = self._fetch_all(rs)
                if rows is None:
                    logger.debug("[MySQL] data not exist")
                    result_list = None
                elif isinstance(rows, list):
                    result_list = rows
                else:
                    result_list = [rows]
                return result_list
        except SQLAlchemyError  as e:
            logger.debug(f"[MySQL] SELECT_LIST Exception : {e}")
            return []

    @parse_query('SELECT')
    def select(self, query_str: str, params=None) -> pd.DataFrame:
        """
        Args:
            query_str(str) : MySQL select query string
            params: query string format parameters like % style, parse_query decorator processing params to query_str
        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        try:
            with self.engine.connect() as conn:
                rs = self._execute_query(conn, query_str, params)
                rows = self._fetch_all(rs)
                if rows:
                    columns = list(rs.keys())
                    return pd.DataFrame(rows, columns=columns)
                else:
                    logger.debug(f"[MySQL] data not exist")
                    return self.empty_dataframe
        except SQLAlchemyError  as e:
            logger.error(f"[MySQL] SELECT Exception : {e}")
            return self.empty_dataframe

    @parse_query('SELECT')
    @log_execution_time
    def faster_select(self, query_str: str, params=None, fetch_size=1000) -> pd.DataFrame:
        """
        Args:
            query_str(str) : MySQL select query string better than normal select
            params: query string format parameters like % style
            fetch_size (int) : size of fetch data
        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        total_size = 0
        results = []
        try:
            with self.engine.connect() as conn:
                # stream_results로 서버사이드 커서 유사 효과
                conn = conn.execution_options(stream_results=True)
                rs = self._execute_query(conn, query_str, params)

                columns = list(rs.keys())  # <-- SQLAlchemy 2.0 스타일로 컬럼명 가져오기

                while True:
                    rows = self._fetch_many(rs, fetch_size)
                    if not rows:
                        break
                    total_size += len(rows)
                    results.extend(rows)
                    if self.use_query_debug:
                        logger.debug(f"fetch {len(rows)} rows, total fetched size = {total_size}")

                if len(results) > 0:
                    return pd.DataFrame(results, columns=columns)
                else:
                    logger.debug(f"[MySQL] data not exist")
                    return self.empty_dataframe
        except SQLAlchemyError  as e:
            logger.debug(f"[MySQL] FASTER_SELECT Exception : {e}")
            self.close()
            return self.empty_dataframe

    # -------------------------
    # Generator (yield) 버전
    # -------------------------
    @parse_query('SELECT')
    def faster_select_generator(self, query_str: str, params=None, fetch_size=1000):
        """
        대량 조회의 제너레이터 버전: DataFrame 청크를 yield 합니다.
        - 메모리 피크를 최소화하고, 소비자 측에서 스트리밍 처리 가능
        - 사용 예:
            for chunk_list in mq.faster_select_generator("SELECT ... WHERE id>%s", (1000,), fetch_size=5000):
                process(chunk_list)
        """
        try:
            with self.engine.connect() as conn:
                conn = conn.execution_options(stream_results=True)
                rs = self._execute_query(conn, query_str, params)
                maps = rs.mappings()

                # 이후 배치
                while True:
                    part = maps.fetchmany(fetch_size)
                    if not part:
                        break
                    rows = [dict(r) for r in part]              
                    if self.use_query_debug:
                        logger.debug(f"fetch {len(rows)} rows chunk")

                    yield rows

        except SQLAlchemyError as e:
            logger.debug(f"[MySQL] faster_select_generotor Exception : {e}")
            # 제너레이터 내부 예외는 호출측에서 캐치 가능하도록 재전파하지 않음
            return

    # ----------------------------------------------------------------------------------
    # INSERT / UPDATE / DELETE
    # ----------------------------------------------------------------------------------
    
    @parse_query('INSERT')
    def insert(self, query_str: str, params=None) -> int:
        """
        Args:
            query_str(str) : MySQL insert query string
            params : query string format parameters like % style, tuple or  list of tuple
        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        try:
            with self.engine.begin() as conn:
                if params is not None and isinstance(params, list) and len(params) > 0:
                    rs = self._execute_query(conn, query_str, params)
                else:
                    rs = self._execute_query(conn, query_str, params)
                rowcount = rs.rowcount if rs.rowcount is not None else 0
                logger.debug(f"[MySQL] INSERT {rowcount} rows")
                return rowcount
        except SQLAlchemyError  as e:
            logger.error(f"[MySQL] INSERT Exception : {e}")
            return 0

    @parse_query('UPDATE')
    def update(self, query_str: str, params=None) -> int:
        """
        Args:
            query_str(str) : MySQL update query string
            params: query string format parameters like % style
        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        try:
            with self.engine.begin() as conn:
                rs = self._execute_query(conn, query_str, params)
                rowcount = rs.rowcount if rs.rowcount is not None else 0
                logger.debug(f"[MySQL] UPDATE {rowcount} rows")
                return rowcount
        except SQLAlchemyError  as e:
            logger.error(f"[MySQL] UPDATE Exception : {e}")
            return 0

    @parse_query('DELETE')
    def delete(self, query_str: str, params=None) -> int:
        """
        Args:
            query_str(str) : MySQL delete query string
            params: query string format parameters like % style

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        try:
            with self.engine.begin() as conn:
                rs = self._execute_query(conn, query_str, params)
                rowcount = rs.rowcount if rs.rowcount is not None else 0
                logger.debug(f"[MySQL] DELETE {rowcount} rows")
                return rowcount
        except SQLAlchemyError  as e:
            logger.debug(f"[MySQL] DELETE Exception : {e}")
            return 0

    # ##################################################################################################
    # 유틸리티 메서드
    # ##################################################################################################
    
    def get_pool_status(self) -> dict:
        """연결 풀 상태 정보 반환"""
        if not self.engine:
            return {"status": "engine not initialized"}
        
        try:
            pool = self.engine.pool
            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid()
            }
        except AttributeError:
            return {"status": "pool information not available"}

    # ----------------------------------------------------------------------------------
    # 종료
    # ----------------------------------------------------------------------------------
    def close(self, close_log=True):
        if self.engine:
            self.engine.dispose()
            self.engine = None
            try:
                if close_log:
                    logger.debug("[MySQL] DB Connection closed.")
            except Exception:
                pass # 인터프리터 종료 중 로거 소멸로 인한 예외 방지

    def __del__(self):
        try:
            self.close(close_log=False)
        except Exception:
            # 절대 예외 전파하지 않음 (GC 단계)
            pass