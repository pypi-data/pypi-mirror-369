from Database import Database
from File import File
from HomeConnection import HomeConnection, HomeWiFi
from Http import Http
from JsonManager import JsonManager
from Mail import Mail
import unittest, time, os
from Common import *
# from Logger import Logger
from commonLogId import *

@versione("1.1.0")
class CustomTestResult(unittest.TextTestResult):
    """ Custom test result to track and categorize test results. """

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)

    def printResults(self):
        self.stream.writeln("\n================== Test Summary ==================")
        
        self.stream.writeln(f"Total tests run: {self.testsRun}")
        self.stream.writeln(f"Successful tests: {len(self.successes)}")
        self.stream.writeln(f"Failed tests: {len(self.failures)}")
        self.stream.writeln(f"Errored tests: {len(self.errors)}")
        
        if self.successes:
            self.stream.writeln("\nSuccessful Tests:")
            for test in self.successes:
                self.stream.writeln(f" - {test.id()}")

        if self.failures:
            self.stream.writeln("\nFailed Tests:")
            for test, err in self.failures:
                self.stream.writeln(f" - {test.id()}: {err}")

        if self.errors:
            self.stream.writeln("\nErrored Tests:")
            for test, err in self.errors:
                self.stream.writeln(f" - {test.id()}: {err}")

@versione("1.1.0")
class CustomTestRunner(unittest.TextTestRunner):
    """ Custom test runner to use the custom result class and print organized output. """
    
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)
    
    def run(self, test):
        result = super().run(test)
        result.printResults()
        return result

@versione("1.1.0")
class PyModules(unittest.TestCase):
    """ Classe che si occupa di effettuare i test di funzionamento dei moduli Python """
    
    @classmethod
    def setUpClass(cls):
        """ Crea un'unica connessione al database per tutti i test della classe """
        LogContext.generate_log_id()
        cls.logger = get_logger(localFileLogPath=f"{os.path.dirname(__file__)}/unitTestLogs", localMode=True)
        cls.logger.info("Inizializzazione dell'unit test")
        cls.db = Database("", "DEV", "monitoring")
        cls.file = File(os.path.dirname(os.path.realpath(__file__)))
        cls.db_ok_time = 0.05
        cls.v = "1.0.1"

    @classmethod
    def tearDownClass(cls):
        """ Chiude la connessione al database dopo che tutti i test sono stati eseguiti """
        cls.db.connection.close()

    def setUp(self):
        # Inizia una transazione
        self.db.connection.start_transaction()

    def tearDown(self):
        # Annulla tutte le modifiche al database fatte durante il test
        self.db.connection.rollback()


    #START UNIT TEST File

    def test_File_read_property(self):
        """ Test lettura property realmente esistente """
        self.file.load_property("unitTest", "DEV")
        expected_result = {"ok": True, "property": ['Test 1', 'test 2', True, 10, 0.55, {'unitTestBool': True, 'unitTestInt': 10, 'unitTestStr': 'Test', 'unitTestFloat': 0.55}], "error": None}
        self.assertEqual(self.file.config, expected_result, "Le property ottenute non sono quelle attese")

    def test_File_read_fantasy_property(self):
        """ Test lettura property inesistente """
        self.file.load_property("unitTest2", "DEV")
        expected_result = {"ok": False, "property": None, "error": "Chiave unitTest2 non trovata nelle property"}
        self.assertEqual(self.file.config, expected_result, "Le property ottenute non sono quelle attese")

    def test_File_read_file(self):
        """ Test lettura file realmente esistente """
        file_content = self.file.read_file("unitTest.txt")
        expected_string = """UnitTest
File

Multiline, this is ok"""
        self.assertEqual(file_content, expected_string)

    def test_File_read_fantasy_file(self):
        """ Test lettura file inesistente """
        file_content = self.file.read_file("unitTest2.txt")
        expected_string = None
        self.assertEqual(file_content, expected_string)


    # END UNIT TEST File

    # -------------------------

    # START UNIT TEST DATABASE

    def test_Database_insert_new_value(self):
        """Testa una insert di un nuovo valore a DB"""
        query = "INSERT INTO elenco_source (nome) VALUES (%s)"
        params = ("unittest",)
        expected_result = {"ok": True, "nrResult": 1, "value_match": []}

        start_time = time.perf_counter()

        result = self.db.doQuery(query, params)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        self.logger.info("Log di test semplicissimo")
        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")
        self.assertTrue(result['ok'], "Errore sull'esecuzione della query")
        self.assertEqual(result['rows_affected'], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertAlmostEqual(result['results'], expected_result['value_match'], "Il valore esatto non è conforme")  
        self.assertIsNone(result['error'], "è stato generato un messaggio di errore inatteso")  

    def test_Database_select_value_unittest(self):
        """Seguito del test insert_new e fa la select"""
        query = "SELECT nome FROM elenco_source WHERE nome = %s"
        params = ("unittest",)
        expected_result = {"ok": True, "nrResult": 1, "value_match": [('unittest',), ()]}
        start_time = time.perf_counter()
        result = self.db.doQuery(query, params)
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")
        self.assertTrue(result['ok'], "Errore sull'esecuzione della query")
        self.assertEqual(result['rows_affected'], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertIn(result['results'][0], expected_result['value_match'], "Il valore esatto non è conforme") 
        self.assertIsNone(result['error'], "è stato generato un messaggio di errore inatteso")

    def test_Database_select_extraspaces_value_unittest(self):
        """Seguito del test insert_new e fa la select"""
        query = """
        
        
                    SELECT nome 
                        FROM elenco_source 
                        WHERE nome = %s
                """
        params = ("unittest",)
        expected_result = {"ok": True, "nrResult": 1, "value_match": [('unittest',), ()]}
        start_time = time.perf_counter()
        result = self.db.doQuery(query, params)
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")
        self.assertTrue(result['ok'], "Errore sull'esecuzione della query")
        self.assertEqual(result['rows_affected'], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertIn(result['results'][0], expected_result['value_match'], "Il valore esatto non è conforme") 
        self.assertIsNone(result['error'], "è stato generato un messaggio di errore inatteso")

    def test_Database_delete_unittest(self):
        """Elimina il valore inserito dalla insert_new"""
        query = "DELETE FROM elenco_source WHERE nome = %s"
        params = ("unittest",)
        expected_result = {"ok": True, "nrResult": 1, "value_match": []}

        start_time = time.perf_counter()
        
        result = self.db.doQuery(query, params)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")
        
        self.assertTrue(result['ok'], "Errore sull'esecuzione della query")
        self.assertEqual(result['rows_affected'], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertAlmostEqual(result['results'], expected_result['value_match'], "Il valore esatto non è conforme") 
        self.assertIsNone(result['error'], "è stato generato un messaggio di errore inatteso")
    
    def test_Database_select_count_function(self):
        """Fa la SELECT con COUNT del valore inserito da insert_new anche se è stato rimosso"""
        query = "SELECT COUNT(nome) FROM elenco_source WHERE nome = %s"
        params = ("unittest",)
        expected_result = {"ok": True, "nrResult": 1, "value_match": [(0,), (1,)]}

        start_time = time.perf_counter()

        result = self.db.doQuery(query, params)

        self.db.execute_query(query, params)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")

        self.assertTrue(result['ok'], "Errore sull'esecuzione della query")
        self.assertEqual(result['rows_affected'], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertIn(result['results'][0], expected_result['value_match'], "Il valore esatto non è conforme")
        self.assertIsNone(result['error'], "è stato generato un messaggio di errore inatteso")

    def test_Database_select_from_fantasy_table(self):
        """Fa la select su una tabella che non esiste"""
        query = "SELECT * FROM pippoplutopaperino WHERE nome = %s"
        params = ("unittest",)
        expected_result = {"ok": True, "nrResult": -1, "value_match": []}

        start_time = time.perf_counter()

        result = self.db.doQuery(query, params)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")

        self.assertFalse(result['ok'], "Esito positivo inatteso, la tabella non esiste")
        self.assertEqual(result['rows_affected'], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertEqual(result['results'], expected_result['value_match'], "Il valore esatto non è conforme")
        self.assertFalse(result['error'] is None, "è stato generato un messaggio di errore inatteso")

    def test_Database_insert_wrong_nr_columns(self):
        """Fa la insert in una tabella che esiste ma con un numero errato di colonne"""
        query = "INSERT INTO elenco_source (nome,id) VALUES (%s,%s)"
        params = ("unittest","666")
        expected_result = {"ok": True, "nrResult": -1, "value_match": []}

        start_time = time.perf_counter()

        result = self.db.doQuery(query, params)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")

        self.assertFalse(result['ok'], "Esito positivo inatteso, la tabella non esiste")
        self.assertEqual(result['rows_affected'], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertEqual(result['results'], expected_result['value_match'], "Il valore esatto non è conforme")
        self.assertFalse(result['error'] is None, "Non è stato generato un messaggio di errore")

    def test_Database_call_procedure(self):
        """Chiama una store procedure con un valore che deve tornare dei risultati"""
        query = "CALL do_unittest"
        params = ("port", -1)
        expected_result = {"ok": True, "nrResult": 1}

        start_time = time.perf_counter()

        result = self.db.doQuery(query, params)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")

        self.assertTrue(result['ok'], "Errore sull'esecuzione della query")
        self.assertGreaterEqual(result['results'][1], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertIsNone(result['error'], "è stato generato un messaggio di errore inatteso")

    def test_Database_call_fantasy_procedure(self):
        """Chiama una store procedure con un valore che deve tornare dei risultati"""
        query = "CALL do_unittest"
        params = ("pipponeplutonetopolino_", -1)
        expected_result = {"ok": True, "nrResult": 0}

        start_time = time.perf_counter()

        result = self.db.doQuery(query, params)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        self.assertLess(elapsed_time, self.db_ok_time, "Tempo di esecuzione query troppo lento")

        self.assertTrue(result['ok'], "Errore sull'esecuzione della query")
        self.assertEqual(result['results'][1], expected_result['nrResult'], "Il numero di righe non è quello atteso")
        self.assertIsNone(result['error'], "è stato generato un messaggio di errore inatteso")

    # END UNIT TEST DATABASE

if __name__ == "__main__":
    # Usa CustomTestRunner per eseguire i test e organizzare l'output
    unittest.main(testRunner=CustomTestRunner(verbosity=2))