import ast
import configparser
import getpass
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Iterator, Union

from edman import DB
from edman.exceptions import EdmanDbConnectError, EdmanDbProcessError


class Action:
    """
    ラッパーやファイル読み込み操作、書き出しなどの操作用
    """
    # DB接続用ファイルのデフォルト設定
    # このクラスはインスタンス化しない前提なので、クラス変数で設定
    setting_ini = 'db'
    ini_ext = '.ini'
    default_ini = setting_ini + ini_ext
    default_ini_dir = 'ini'

    @staticmethod
    def file_gen(files: tuple[Path]) -> Union[Iterator[dict], Iterator[str]]:
        """
        ファイルタプルからデータを取り出すジェネレータ
        XMLならstr、jsonなら辞書を返す

        :param tuple files:中身はPathオブジェクト
        :return: read_data
        :rtype: dict or str
        """
        for file in files:

            if 'xml' in file.suffix:
                try:
                    with file.open() as f:
                        read_data = f.read()
                        print(f'{str(file)} '
                              f'Converting from XML to dictionary...')
                except IOError:
                    sys.exit(f'File is not read. {str(file)}')
                yield read_data

            if 'json' in file.suffix:
                try:
                    with file.open(encoding='utf8') as f:
                        read_data = json.load(f)
                        print(f'Processing to {file}')
                except json.JSONDecodeError:
                    sys.exit(f'File is not json format. {file}')
                yield read_data

    @staticmethod
    def files_read(file_or_dir_path: Union[str, Path], suffix=None) -> (
            tuple)[Path, ...]:
        """
        ファイルのパスを、
        単一ファイルもディレクトリ内の複数ファイルもタプルにして返す
        拡張子の指定をすると、ディレクトリ内の該当のファイルのみ取得

        :param file_or_dir_path:
        :type file_or_dir_path: str or Path
        :param suffix:
        :type suffix: str or None
        :return: files
        :rtype: tuple
        """
        if isinstance(file_or_dir_path, str):
            p = Path(file_or_dir_path)
        elif isinstance(file_or_dir_path, Path):
            p = file_or_dir_path
        else:
            sys.exit('file_read() is a str or path Object is required.')

        if not p.exists():
            sys.exit('That path does not exist.')

        if suffix is None:
            files = tuple(sorted(p.glob('*'))) if p.is_dir() else (p,)
            message = ''
        else:
            files = (
                tuple(sorted(p.glob(f'*.{suffix}')))
                if p.is_dir() else (p,)
                if f'.{suffix}' in p.suffix else tuple()
            )
            message = suffix

        if not len(files):
            sys.exit(f'{message} files not in directory.')

        return files

    @staticmethod
    def query_eval(raw_query: str) -> dict:
        """
        文字列のクエリを受け取り、辞書に変換する

        :param str raw_query:
        :return: query
        :rtype: dict
        """
        error_message = 'クエリが正しくありません。\"{}\"で囲みpythonの辞書形式にしてください'
        try:
            query = ast.literal_eval(raw_query)
        except SyntaxError:
            sys.exit(error_message)
        if not isinstance(query, dict):
            sys.exit(error_message)
        return query

    @staticmethod
    def file_query_eval(raw_query: str, structure: str) -> list | None:
        """
        embの場合文字列のクエリを受け取り、リストに変換する
        refの場合はNoneを返す

        :param str raw_query:
        :param str structure:
        :return: query
        :rtype: list or None
        """
        # embのときだけクエリが必須
        if 'ref' in structure:
            query = None
        elif 'emb' in structure:
            if raw_query is None:
                sys.exit('クエリがありません')
            # embの時はリストに変換
            error_message = 'クエリがリスト形式ではありません.'
            try:
                query = ast.literal_eval(raw_query)
            except SyntaxError:
                sys.exit(error_message)
            if not isinstance(query, list):
                sys.exit(error_message)
        else:
            sys.exit('ref or embを指定してください')
        return query

    @staticmethod
    def create(admin: dict, user: dict, ini_dir: Path, host='127.0.0.1',
               port=27017, ldap=False) -> None:
        """
        ユーザ権限のDBを作成する

        :param dict admin: 管理者のユーザ情報
        :param dict user: 作成するユーザ情報
        :param str host: ホスト名
        :param int port: 接続ポート
        :param Path ini_dir: 接続情報用iniファイルの格納場所
        :param bool ldap:
        :return:
        """
        # admin接続でDBクラスをインスタンス化
        adminauth = admin['name']
        admin_ini = {
            'user': admin['name'],
            'host': host,
            'port': port,
            'database': admin['dbname'],
            'password': admin['pwd'],
            'options': [f'authSource={adminauth}']
        }
        try:
            admin_cl = DB(admin_ini)
        except EdmanDbConnectError:
            sys.exit('DB not connect.')

        # 重複するデータは登録できないので予め阻止
        d = admin_cl.get_db
        if d['system.users'].count_documents(
                {
                    '$or': [
                        {'user': user['name']},
                        {'db': user['dbname']}
                    ]
                }):
            sys.exit('user name or user db is duplicated.')

        # iniファイル書き出し処理
        if ini_dir is not None:
            ini_data = {
                'host': host,
                'port': port,
                'username': user['name'],
                'dbname': user['dbname']
            }
            if not ldap:
                ini_data['userpwd'] = user['pwd']
                ini_data['auth_dbname'] = user['dbname']

            Action.create_ini(ini_data, ini_dir, ldap)

        # 指定のDB、ユーザ、もしくはロールを作成
        try:
            if ldap:
                admin_cl.create_role(user['dbname'], user['name'])
            else:
                admin_cl.create_user_and_role(user['dbname'], user['name'],
                                              user['pwd'])
        except EdmanDbProcessError:
            sys.exit('DB,User/Role creation failed.')
        else:
            print('DB,User/Role Create OK.')

    @staticmethod
    def create_ini(ini_data: dict, ini_dir: Path, ldap=False) -> None:
        """
        指定のディレクトリにiniファイルを作成
        同名ファイルがあった場合はname_[file_count +1].iniとして作成

        :param dict ini_data: 接続情報用iniファイルに記載するデータ
        :param Path ini_dir: 格納場所
        :param bool ldap:
        :return:
        """
        # この値は現在固定
        dup_flg, proposal_filename = Action.is_duplicate_filename(ini_dir)
        if dup_flg:
            filename = proposal_filename
            print(
                f'{Action.default_ini} is exists.Create it as a [{filename}].')
        else:
            filename = Action.default_ini

        if ldap:
            put_data = [
                '[DB]',
                '# DB user settings\n',
                '# MongoDB default port 27017',
                f"port = {str(ini_data['port'])}" + '\n',
                '# MongoDB server host',
                f"host = {ini_data['host']}" + '\n',
                f"user = {ini_data['username']}",
                f"database = {ini_data['dbname']}",
                'options = ["authMechanism=PLAIN"]' + '\n'
            ]
        else:
            # iniファイルの内容
            authsource = f"authSource={ini_data['auth_dbname']}"
            put_data = [
                '[DB]',
                '# DB user settings\n',
                '# MongoDB default port 27017',
                f"port = {str(ini_data['port'])}" + '\n',
                '# MongoDB server host',
                f"host = {ini_data['host']}" + '\n',
                f"user = {ini_data['username']}",
                f"password = {ini_data['userpwd']}",
                f"database = {ini_data['dbname']}",
                f'options = ["{authsource}"]' + '\n'
            ]

        # iniファイルの書き出し
        savefile = ini_dir / filename  # type: ignore
        try:
            with savefile.open("w") as file:
                file.writelines('\n'.join(put_data))
                file.flush()
                os.fsync(file.fileno())

                print(f'Create {savefile}')
        except IOError:
            print('ini file not create.Please create it manually.')

    @staticmethod
    def destroy(user: dict, host: str, port: int, admin,
                ldap=False) -> None:
        """
        DBとユーザもしくはロールを削除する
        管理者権限が必要

        :param dict user: 削除対象のユーザデータ
        :param str host: ホスト名
        :param int port: ポート番号
        :param dict admin:
        :param bool ldap:
        :return:
        """
        # admin接続でDBクラスをインスタンス化
        adminauth = admin['name']
        admin_ini = {
            'user': admin['name'],
            'host': host,
            'port': port,
            'database': admin['dbname'],
            'password': admin['pwd'],
            'options': [f'authSource={adminauth}']
        }
        try:
            db = DB(admin_ini)
        except EdmanDbConnectError:
            sys.exit('DB not connect.')

        # ユーザもしくはロールが存在するかどうか
        d = db.get_db
        if ldap:
            target_collection = 'system.roles'
            find_value = {'role': user['name']}
            err_message = f"Role name {user['name']}"
        else:
            target_collection = 'system.users'
            find_value = {'user': user['name']}
            err_message = f"User name {user['name']}"
        if not d[target_collection].find(find_value):
            sys.exit(f"{err_message}, does not exist.")

        # DB,ロールもしくはユーザ削除
        try:
            if ldap:
                db.delete_role(user['name'], user['dbname'])
                db.delete_db(user['dbname'])
            else:
                db.delete_user_and_role(user['name'], user['dbname'])
                db.delete_db(user['dbname'])
        except EdmanDbProcessError:
            sys.exit('DB,User/Role delete failed.')
        except EdmanDbConnectError:
            sys.exit('DB not connect.')
        except Exception as e:
            sys.exit(str(e))
        else:
            print('DB,User/Role delete OK.')

    @staticmethod
    def is_duplicate_filename(ini_dir: Path) -> tuple[bool, Union[str, None]]:
        """
        ini_dirのパスに指定のファイルが存在していれば重複のフラグ、
        及びfilename[+_number].iniを出力

        :param Path ini_dir:
        :return:
        :rtype: tuple
        """
        ini_files = tuple(
            [i.name for i in
             tuple(ini_dir.glob(Action.setting_ini + '*' + Action.ini_ext))])

        if Action.default_ini in ini_files:
            proposal_filename = Action.setting_ini + '_' + str(
                len(ini_files) + 1) + Action.ini_ext
            return True, proposal_filename
        else:
            return False, None

    @staticmethod
    def generate_account(user: str, ldap=False) -> dict:
        """
        DBアカウント作成のための画面表示

        :param str user:
        :param bool ldap:
        :return: account
        :rtype: dict
        """
        acc = OrderedDict()
        acc['name'] = f"MongoDB's {user} name >> "
        acc['dbname'] = f"MongoDB's {user} DB >> "

        if not ldap:
            acc['pwd'] = f"MongoDB's {user} password >> "
            acc['pwd_verification'] = (f"MongoDB's {user} "
                                       f"Verification password >> ")

        account: dict = {}
        for key, value in acc.items():
            buff = ""
            if 'name' == key or 'dbname' == key:
                while True:
                    if not (buff := input(value)):
                        print('Required!')
                    else:
                        break
            else:
                if not ldap:
                    if 'pwd' == key:
                        while True:
                            if not (buff := getpass.getpass(value)):
                                print('Required!')
                            else:
                                break
                    elif 'pwd_verification' == key:
                        while True:
                            if account['pwd'] != (
                                    buff := getpass.getpass(value)):
                                print('Do not match!')
                            else:
                                break
            account[key] = buff

            if account.get('pwd_verification'):
                del account['pwd_verification']

        return account

    @staticmethod
    def value_output(user: str, user_data: dict) -> None:
        """
        DB入力項目の確認表示(アカウント項目)

        :param str user:
        :param dict user_data:
        :return:
        """
        print(f'[{user}]')
        for key, value in user_data.items():
            print(key + ' : ' + '*' * len(
                value) if key == 'pwd' else key + ' : ' + value)

    @staticmethod
    def outputs(users: dict, host: str, port: int,
                ini_dir: Path | None) -> None:
        """
            DB入力項目の確認表示(サーバ項目)

        :param dict users:
        :param str host:
        :param int port:
        :param Path or None ini_dir:
        :return:
        """
        # 入力値出力
        for user, user_data in users.items():
            Action.value_output(user, user_data)
        print(f"""
        host : {host}
        port : {port}
        """)
        if ini_dir is not None:
            dup_flg, proposal_filename = Action.is_duplicate_filename(ini_dir)
            filename = proposal_filename if dup_flg else Action.default_ini
            ini_path = ini_dir / filename  # type: ignore
            print(f"ini path : {ini_path}")

    @staticmethod
    def generate_config_path(filepath: Union[str, None]) -> Path:
        """
        パス文字列からパスオブジェクト生成
        パス文字列がなければデフォルトのiniディレクトリパスを返す

        :param str or None filepath:
        :return: result
        :rtype: Path
        """
        if filepath is not None:
            p = Path(filepath)
            if p.exists():
                result = p
            else:
                sys.exit(f'{filepath}は存在しません')
        else:
            result = Path.cwd() / Action.default_ini_dir / Action.default_ini

        return result

    @staticmethod
    def reading_config_file(input_file: Union[str, None]) -> dict:
        """
        設定ファイルを読み込み、辞書として返す

        :param str or None input_file:
        :return:
        :rtype: dict
        """
        settings = configparser.ConfigParser()
        settings.read(Action.generate_config_path(input_file))
        result = {k: json.loads(v) if k == 'options' else v for k, v in
                  settings['DB'].items()}
        return result
