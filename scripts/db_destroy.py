def main():
    """
    DBと認証ユーザを削除する
    """
    import argparse
    import signal
    import sys

    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(
        description='DB及びDB管理ユーザ/管理ロール削除スクリプト')
    parser.add_argument('-r', '--remove_role',
                        help='Remove DB and role(LDAP User),MongoDB Admin account required.',
                        action='store_true')

    # 引数を付けなかった場合はヘルプを表示して終了する
    # if len(sys.argv) == 1:
    #     parser.parse_args(["-h"])
    #     sys.exit(0)

    args = parser.parse_args()
    try:
        # 管理者アカウント入力
        admin_account = Action.generate_account("Admin")

        # ユーザアカウント入力
        # 削除するのはadminなのでユーザのパスワードの入力は問われない、したがってldap=Trueにしている
        user_account = Action.generate_account('user', ldap=True)

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

        # 入力値表示
        Action.value_output('admin', admin_account)
        Action.value_output('user', user_account)
        print(f"""
        host : {host}
        port : {port}
        """)
        print(user_account['dbname'], 'is Erase all data.')
        while True:
            confirm = input('OK? y/n(exit) >>')
            if confirm == 'n':
                sys.exit('exit')
            elif confirm == 'y':
                break
            else:
                continue

        # DBの削除
        Action.destroy(user_account, host, port, admin=admin_account,
                       ldap=args.remove_role)

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
