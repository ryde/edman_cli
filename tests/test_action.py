import sys
import tempfile
import shutil
import json
import configparser
from pathlib import Path
from unittest import TestCase, skipIf

# edman/scripts/action.pyが読み込める状態ならテストをする
# それ以外なら全てのテストをスキップする
cwd = Path.cwd()
import_path = cwd.parent / 'scripts'
import_path_full = import_path / 'action.py'
if import_path_full.exists():
    sys.path.append(str(import_path))
    from action import Action

    import_flag = True
else:
    import_flag = False


class TestAction(TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     pass
    #
    # @classmethod
    # def tearDownClass(cls):
    #     pass
    #
    # def setUp(self):
    #     pass

    @skipIf(import_flag is False, 'There is no action.py')
    def test_file_gen(self):

        # 正常系 xml
        xml_data = ('<?xml version="1.0" encoding="UTF-8" ?>'
                    '<foods>'
                    '<food>'
                    '<name>banana</name>'
                    '<color>yellow</color>'
                    '</food>'
                    '<food>'
                    '<name>apple</name>'
                    '<color>red</color>'
                    '</food>'
                    '</foods>')
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml') as fp:
            fp.write(xml_data)
            fp.seek(0)
            xml_path = (Path(fp.name),)
            for i in Action.file_gen(xml_path):
                self.assertEqual(i, xml_data)

        # 正常系 json
        json_data = ('{"Sport":[{"D1":"Japan"},'
                     '{"WRC":"Safari","F1":"Monaco"}]}')
        expected = json.loads(json_data)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as fp:
            fp.write(json_data)
            fp.seek(0)
            json_path = (Path(fp.name),)
            for i in Action.file_gen(json_path):
                self.assertEqual(i, expected)

        # JSONデコードエラー時
        json_data = ('{"Sport":[{"D1":"Japan"},'
                     '{"WRC":"Safari","F1":"Monaco}]}')
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as fp:
            fp.write(json_data)
            fp.seek(0)
            json_path = (Path(fp.name),)
            with self.assertRaises(SystemExit):
                for i in Action.file_gen(json_path):
                    print(i)

    @skipIf(import_flag is False, 'There is no action.py')
    def test_files_read(self):

        # 単一ファイルの場合
        with tempfile.NamedTemporaryFile() as fp:
            filename = fp.name
            actual = Action.files_read(filename)
        expected = (Path(filename),)
        self.assertTupleEqual(actual, expected)

        # 複数ファイル(json+その他)の場合
        tmpdir = tempfile.TemporaryDirectory()
        jsons = 4
        texts = 1
        for i in range(jsons):
            with tempfile.NamedTemporaryFile(suffix='.json') as fp:
                shutil.copy(fp.name, tmpdir.name)

        for i in range(texts):
            with tempfile.NamedTemporaryFile(suffix='.txt') as fp:
                shutil.copy(fp.name, tmpdir.name)

        actual = Action.files_read(tmpdir.name, suffix='json')
        expected = jsons
        tmpdir.cleanup()
        self.assertEqual(len(actual), expected)

        # 指定した拡張子のファイルがディレクトリ内に存在しない場合
        # 単一ファイルの場合
        with tempfile.NamedTemporaryFile() as fp:
            with self.assertRaises(SystemExit):
                _ = Action.files_read(fp.name, suffix='jpg')

        # ディレクトリにファイルがない場合
        with tempfile.TemporaryDirectory() as tmpdir_name:
            with self.assertRaises(SystemExit):
                _ = Action.files_read(tmpdir_name)

        # パスオブジェクトでない場合
        with self.assertRaises(SystemExit):
            _ = Action.files_read('test')

    @skipIf(import_flag is False, 'There is no action.py')
    def test_query_eval(self):

        # 正常系
        strings = "{'Name':'NSX', 'Power':'280', 'Maker':'Honda'}"
        actual = Action.query_eval(strings)
        self.assertIsInstance(actual, dict)
        expected = {'Name': 'NSX', 'Power': '280', 'Maker': 'Honda'}
        self.assertDictEqual(actual, expected)

        # 変換できない場合
        strings = "{'Name':'NSX',"
        with self.assertRaises(SystemExit):
            _ = Action.query_eval(strings)

        # 辞書でない場合
        strings = "['yamato', 'atom']"
        with self.assertRaises(SystemExit):
            _ = Action.query_eval(strings)

    @skipIf(import_flag is False, 'There is no action.py')
    def test_file_query_eval(self):
        # 正常系 embかつリスト
        input_list = "['top', 'middle', 'parent']"
        actual = Action.file_query_eval(input_list, 'emb')
        self.assertIsInstance(actual, list)
        expected = ['top', 'middle', 'parent']
        self.assertListEqual(actual, expected)

        # 正常系 refの時
        actual = Action.file_query_eval(None, 'ref')
        self.assertIsNone(actual)

        # emb eval失敗
        input_list = "['top', 'middle', 'paren"
        with self.assertRaises(SystemExit):
            _ = Action.file_query_eval(input_list, 'emb')

        # embなのにリストでない
        input_list = "{'name':'JJ', 'age':'22', 'flg':'True'}"
        with self.assertRaises(SystemExit):
            _ = Action.file_query_eval(input_list, 'emb')

        # embなのにクエリがない
        with self.assertRaises(SystemExit):
            _ = Action.file_query_eval(None, 'emb')

        # 構造がrefとemb以外の時
        with self.assertRaises(SystemExit):
            input_list = "['top', 'middle', 'parent']"
            _ = Action.file_query_eval(input_list, 'types')

    @skipIf(import_flag is False, 'There is no action.py')
    def test_create_ini(self):
        # データ作成
        data = {
            'host': '127.0.0.1',
            'port': 27017,
            'username': 'username',
            'userpwd': 'userpwd',
            'dbname': 'userdb',
            'auth_dbname': 'userdb'
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir)

            Action.create_ini(data, p)

            # 実際にファイルがあるかテスト
            dbfile_path = p / 'db.ini'
            self.assertTrue(dbfile_path.exists())

            # ファイルの中身があっているかテスト
            a = configparser.ConfigParser()
            a.read(dbfile_path)
            actual_db = dict([i for i in a['DB'].items()])

            expected_db = {
                'port': '27017',
                'host': '127.0.0.1',
                'database': 'userdb',
                'auth_database': 'userdb',
                'user': 'username',
                'password': 'userpwd'}

            self.assertDictEqual(actual_db, expected_db)

            # 連続したファイルを生成した場合のテスト
            files_count = 2
            for i in range(files_count):
                Action.create_ini(data, p)
            ps = sorted(p.glob('*.ini'))
            self.assertEqual(files_count + 1, len(ps))

    @skipIf(import_flag is False, 'There is no action.py')
    def test_is_duplicate_filename(self):

        # 重複しない場合
        with tempfile.TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir)
            dup_flg, proposal_filename = Action.is_duplicate_filename(p)
            self.assertFalse(dup_flg)
            self.assertIsNone(proposal_filename)

        # 重複する場合
        with tempfile.TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir)
            file_path = p / 'db.ini'
            with file_path.open("w") as f:
                f.write('test')
            dup_flg, proposal_filename = Action.is_duplicate_filename(p)
            self.assertTrue(dup_flg)
            self.assertEqual(proposal_filename, 'db_2.ini')

    @skipIf(import_flag is False, 'There is no action.py')
    def test_generate_config_path(self):

        with tempfile.TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir)
            file_path = p / 'db.ini'
            with file_path.open("w") as f:
                f.write('test')
            p2 = str(Path(file_path))
            actual = Action.generate_config_path(p2)
            self.assertIsInstance(actual, Path)

    @skipIf(import_flag is False, 'There is no action.py')
    def test_reading_config_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            p = Path(tmp_dir)
            file_path = p / 'db.ini'
            with file_path.open("w") as f:
                f.write('[DB]\nname=admin\npwd=abcd')
            p2 = str(Path(file_path))
            actual = Action.reading_config_file(p2)
            expected = {'name': 'admin', 'pwd': 'abcd'}
            self.assertDictEqual(actual, expected)

            # デフォルトの場合
            # actual = Action.reading_config_file(None)
            # print(actual)
            # expected = {}
            # self.assertDictEqual(actual, expected)

    # @skipIf(import_flag is False, 'There is no action.py')
    # def test_create(self):
    #     pass
    #     # 本筋の機能ではないためテストは割愛
    #
    # @skipIf(import_flag is False, 'There is no action.py')
    # def test_destroy(self):
    #     pass
    #     # 本筋の機能ではないためテストは割愛
