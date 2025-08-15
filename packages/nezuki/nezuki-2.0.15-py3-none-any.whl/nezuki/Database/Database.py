import datetime
import json
import os
from re import S
import typing
import mysql.connector
import psycopg
from psycopg.rows import dict_row
import asyncpg
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()  # Usa il logger corretto

class Database:
    """
    Crea la connessione al Database e permette di eseguire qualsiasi query safe e non safe.

    Attributes:
        database (str): Nome del database a cui connettersi.
        connection: Connessione persistente al DB (istanza di mysql.connector.MySQLConnection o psycopg connection).
        db_type (str): Tipo di database, 'mysql' o 'postgresql'.
        auto_load (bool): Se True, la connessione viene caricata automaticamente.
        errorDBConnection (bool): Flag per indicare errori di connessione.
    """

    database: str
    """ Nome del Database al quale ci si vuole collegare"""

    connection: mysql.connector.MySQLConnection
    """ Connessione persistente al DB """

    configJSON: dict
    """ INTERNAL: Confgiruazioni di connessione al DB """
    
    def __init__(self, database: str = "monitoring", db_type: typing.Literal["mysql", "postgresql"] = "mysql") -> None:
        """ Inizializza l'oggetto Database.

        Args:
            database (str): Il nome del database (default "monitoring").
            db_type (str): Il tipo di database ("mysql" o "postgresql", default "mysql").
        """
        self.database = database
        self.db_type = db_type.lower()
        self.auto_load = False
        self.errorDBConnection = False
        self.configJSONNew = None
        self.async_conn = False

    async def as_start_connection(self):
        """
        Avvia la connessione al Database Asincrona
        """
        self.async_conn = True
        self.__load_configuration__()
        if self.db_type == "postgresql":
            logger.debug("Avvio connessione PostgreSQL", extra={"internal": True})
            return asyncpg.connect(**self.configJSONNew)
        else:
            raise ValueError(f"Tipo di Database non supportato: {self.db_type}")

    def connection_params(self, host: str, user: str, password: str, port: int=None) -> dict:
        """
        Configura manualmente i parametri di connessione al database.

        Args:
            host (str): Indirizzo del server DB.
            user (str): Nome utente per la connessione.
            password (str): Password per la connessione.
            port (int): Porta da usare, se non passata verrà usata la porta standard per il tipo di DB

        Returns:
            dict: I parametri di connessione impostati (potresti voler ritornare il dizionario o semplicemente aggiornare l'oggetto).
        """
        self.auto_load = False

        # Gestiamo la porta standard
        if port is None:
            if self.db_type == "mysql":
                port = 3306
            elif self.db_type == "postgresql":
                port: 5432

        self.configJSONNew: dict = {
            "database": self.database,
            "host": host,
            "user": user,
            "password": password,
            "port": port
        }
        if self.db_type == "postgresql":
            self.configJSONNew['dbname'] = self.database
            self.configJSONNew.pop('database')
        try:
            logger.debug("Avvio la connessione al DB con i parametri", extra={"internal": True})
            self.connection = self.start_connection()
            self.errorDBConnection = False
            logger.debug("Connessione al DB avvenuta con successo", extra={"internal": True})
        except Exception as e:
            logger.error(f"Connessione al DB fallita. {e}", extra={"internal": True})
            raise e
    
    def start_connection(self):
        """
        Avvia la connessione al Database
        """
        if self.db_type == "mysql":
            logger.debug("Avvio connessione MySQL", extra={"internal": True})
            return mysql.connector.connect(**self.configJSONNew)
        elif self.db_type == "postgresql":
            logger.debug("Avvio connessione PostgreSQL", extra={"internal": True})
            return psycopg.connect(**self.configJSONNew)
        else:
            raise ValueError(f"Tipo di Database non supportato: {self.db_type}")
        
    def __load_configuration__(self):
        logger.info("Carico connessione al DB da $NEZUKIDB", extra={"internal": True})
        self.auto_load = True
        from nezuki.JsonManager import JsonManager
        json_config = JsonManager()
        db_config:str = os.getenv('NEZUKIDB')
        self.configJSONNew = json_config.read_json(db_config)
        self.configJSONNew['database'] = self.database
        if self.db_type == "postgresql":
            logger.info("Creo py")
            self.configJSONNew['dbname'] = self.database
            self.configJSONNew.pop('database')
        if not self.async_conn:
            try:
                self.connection = self.start_connection()
            except Exception as e:
                logger.debug(f"Property connessione: {self.configJSONNew}", extra={"internal": True})
                logger.error("Property caricate, connessione fallita", extra={"internal": True})
                raise e
                self.errorDBConnection = True
            
    def __rollback_safely__(self):
        try:
            if hasattr(self, "connection") and self.connection:
                # Valido per MySQL e PostgreSQL
                if getattr(self.connection, "autocommit", None) is False:
                    logger.error("Eseguo ROLLBACK immediato e liberare il lock su DB", extra={"internal": True})
                    self.connection.rollback()
        except Exception as _:
            pass  # Evita che un errore in rollback nasconda l'errore originale
    
    def __sanitize_string__(self, text: str) -> str:
        """
        Effettua una trim del testo passato in input.
        
        Args:
            text (str): testo su cui applicare la trim
            
        Returns:
            str: La stringa con la trim dagli spazi iniziali e finali"""
        to_ret: str = text.strip()
        return to_ret
    
    def __internal_execute_query__(self, query: str, params=None, namedOutput: bool=False) -> dict:
        """
        Esegue una query in modo sicuro con commit/rollback e logging unificati.

        Args:
            query (str): Query parametrica da eseguire.
            params (tuple|list|dict|None): Parametri per la query.
            namedOutput (bool): Se True, il risultato (solo per SELECT) include i nomi dei campi (dict).
                                Se False, ritorna righe "raw" (tuple in MySQL, tuple/dictcursor in PG).

        Returns:
            dict: {"ok": bool, "results": list, "rows_affected": int, "error": str|None, "lastrowid": int|None}
        """
        if self.configJSONNew is None:
            self.__load_configuration__()
            msg = "Connessione al DB fatta mediante variabile env NEZUKIDB"
            if not self.errorDBConnection:
                logger.debug(msg, extra={"internal": True})
            else:
                logger.error(msg, extra={"internal": True})

        if self.errorDBConnection or self.configJSONNew is None:
            if self.errorDBConnection:
                err_msg: str = "Non è possibile eseguire query con una connessione fallita"
            elif self.configJSONNew is None: 
                err_msg: str = "Non è possibile eseguire query con la configurazione di connessione a DB assente"
            logger.error(err_msg, extra={"internal": True})
            return {"ok": False, "results": [], "rows_affected": -1, "error": err_msg, "lastrowid": None}

        query = self.__sanitize_string__(query)

        # Determina tipologia query
        first_kw = query.upper().split(None, 1)[0] if query else ""
        is_select = first_kw == "SELECT"
        is_write  = first_kw in {"INSERT", "UPDATE", "DELETE"}
        is_call   = first_kw == "CALL"

        logger.debug(
            f"Esecuzione query ({'named' if namedOutput else 'raw'}) - tipo: "
            f"{'SELECT' if is_select else ('DML' if is_write else ('CALL' if is_call else first_kw))}",
            extra={"internal": True}
        )

        # Scegli il cursor
        cursor = None
        try:
            if self.db_type == "postgresql":
                if namedOutput:
                    # Dizionari con nomi colonna
                    cursor = self.connection.cursor(row_factory=dict_row)  # list[dict]
                else:
                    # Righe "raw" (ma DictCursor restituisce mapping; se preferisci tuple usa cursor semplice)
                    cursor = self.connection.cursor()  # list[tuple]
            else:  # MySQL
                # In MySQL per namedOutput trasformiamo manualmente dopo il fetch
                cursor = self.connection.cursor(buffered=True)

            results = []
            lastrowid = None

            if is_call:
                # callproc vuole il nome (non "CALL ...")
                if self.db_type == "postgresql":
                    proc_name = query.replace("CALL", "", 1).strip().split("(")[0]
                    cursor.callproc(proc_name, params or [])
                else:
                    proc_name = query.replace("CALL", "", 1).strip()
                    cursor.callproc(proc_name, params or [])
                rows = 0  # dipende dalla proc; qui non presumiamo resultset
            else:
                cursor.execute(query, params)

                # Ci sono righe in output?
                has_rows = (cursor.with_rows if self.db_type == "mysql" else cursor.description is not None)

                if is_select and has_rows:
                    if self.db_type == "postgresql":
                        fetched = cursor.fetchall()
                        # RealDictCursor --> list[dict]; DictCursor --> list[DictRow] (mappabile)
                        results = list(fetched)
                    else:
                        fetched = cursor.fetchall()
                        if namedOutput and cursor.description:
                            columns = [d[0] for d in cursor.description]
                            results = [dict(zip(columns, row)) for row in fetched]
                        else:
                            results = list(fetched)

                rows = cursor.rowcount

                if is_write:
                    # DML -> commit
                    self.connection.commit()
                    logger.debug("Eseguo l'auto COMMIT su DB", extra={"internal": True})
                    if self.db_type == "mysql":
                        try:
                            lastrowid = cursor.lastrowid
                        except Exception:
                            lastrowid = None
                else:
                    # Evita idle-in-transaction anche per SELECT o altri statement non-DML
                    if self.db_type == "postgresql" and getattr(self.connection, "autocommit", False) is False:
                        try:
                            self.connection.commit()
                        except Exception:
                            # in caso di SELECT in sola lettura il commit è innocuo; se fallisse, proviamo rollback
                            self.__rollback_safely__()
            logger.debug(f"Output query: {results}", extra={"internal": True})
            # Normalizza datetime -> ISO string quando namedOutput (solo se i risultati sono dict)
            if namedOutput and results and isinstance(results[0], dict):
                for row in results:
                    for k, v in list(row.items()):
                        if isinstance(v, datetime.datetime):
                            row[k] = v.isoformat()
            to_ret: dict = {"ok": True, "results": results, "rows_affected": rows, "error": None, "lastrowid": lastrowid}

            logger.debug(f"Ritorno finale query: {to_ret}", extra={"internal": True})
            return to_ret

        except Exception as e:
            # Rollback + log
            self.__rollback_safely__()
            logger.error(
                f"Errore durante l'esecuzione della query ({'named' if namedOutput else 'raw'}), "
                f"tipo: {first_kw}, errore: {e}. Query: {query} Params: {params}",
                extra={"internal": True}
            )
            return {"ok": False, "results": [], "rows_affected": -1, "error": str(e), "lastrowid": None}
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
        
    
    def doQuery(self, query: str, params = None) -> dict :
        """
        Funzione wrapper per eseguire query con output di tipo tuple(tuple) quindi è un array di risultati

        Args:
            query (str): La query da eseguire. Se sono presenti parametri, utilizzare %s per placeholder.
            params: Parametri da passare alla query, nel formato `tuple` e, in caso di un solo parametro, mettere la virgola dopo il primo elemento `tuple`

        Returns:
            dict: Un dizionario con la struttura:
                  {"ok": Bool, "results": list(list), "rows_affected": int, "error": None|str, "lastrowid": Optional[int]}
        """
        return self.__internal_execute_query__(query, params=params, namedOutput=False)
        
    def doQueryNamed(self, query: str, params=None) -> dict:
        """
        Funzione wrapper per eseguire query con output di tipo tuple di dizionario quindi è un array di JSON

        Args:
            query (string, required): La query da eseguire. Se sono presenti parametri, utilizzare %s per placeholder.
            params (tuple, optional): Parametri da passare alla query, nel formato `tuple`.

        Returns:
            dict: Un dizionario con la struttura:
                {"ok": Bool, "results": list(dict), "rows_affected": int, "error": None|str, "lastrowid": Optional[int]}
        """

        return self.__internal_execute_query__(query, params=params, namedOutput=True)
    
    def __del__(self) -> None:
        """ Chiude la connessione al DB se è stata inizializzata """
        if hasattr(self, "connection") and self.connection:
            self.connection.close()