def main():
    """
    新しいユーザ権限のDBを作成
    """
    import argparse
    import signal
    import sys
    from pathlib import Path

    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='MongoDBのユーザとDBを作成するスクリプト')
    parser.add_argument('-n', '--not_ini', action='store_false',
                        help='Do not create db.ini.')
    parser.add_argument('-d', '--db_only', action='store_true',
                        help='DB and Role create only(for LDAP User).')

    # 引数を付けなかった場合はヘルプを表示して終了する
    # if len(sys.argv) == 1:
    #     parser.parse_args(["-h"])
    #     sys.exit(0)
    args = parser.parse_args()

    try:
        # 管理者アカウント入力
        admin_account = Action.generate_account("Admin")

        # ユーザアカウント入力
        user_account = Action.generate_account("User", ldap=args.db_only)

        if args.not_ini:
            # iniセーブパス入力
            while True:
                ini_input = input("db.ini save path(Absolute or Relative) >> ")
                p = Path(ini_input)
                if not ini_input:
                    print('Required!')
                elif (not p.exists()) or (not p.is_dir()):
                    print('path is invalid')
                else:
                    ini_dir = p.resolve()
                    dup_flg, proposal_name = Action.is_duplicate_filename(
                        ini_dir)
                    if dup_flg:
                        print(
                            f'Create in {proposal_name}'
                            f', because the file name is duplicated.')
                    break
        else:
            ini_dir = None

        # ホスト名入力(デフォルト設定あり)
        host = input(
            "MongoDB's host (Enter to skip, set 127.0.0.1) >> ") or '127.0.0.1'

        # ポート入力(デフォルト設定あり)
        while True:
            port = input("MongoDB's port (Enter to skip, set 27017) >> ")
            if len(port) == 0:
                port = 27017
                break
            elif not port.isdigit():
                print('input port(number)')
            elif not (1024 <= int(port) <= 49151):
                print('input user port.')
            else:
                port = int(port)
                break

        # 最終確認
        Action.outputs({'Admin': admin_account, 'User': user_account}, host,
                       port, ini_dir)

        while True:
            confirm = input('OK? y/n(exit) >>')
            if confirm == 'n':
                sys.exit('exit')
            elif confirm == 'y':
                break
            else:
                continue

        # DB作成
        Action.create(admin_account, user_account, ini_dir, host, port,
                      ldap=args.db_only)

        # テスト用のためにここに置く
        # db.destroy(user_account, host, port, admin=admin_account,
        # del_user=True)

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
