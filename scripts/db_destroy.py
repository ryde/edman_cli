def main():
    """
    DBと認証ユーザを削除する
    """
    import sys
    import signal
    import argparse
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='DB及びDB管理ユーザ削除スクリプト')
    parser.add_argument('-ru', '--remove_user',
                        help='Remove DB user,MongoDB Admin account required.',
                        action='store_true')

    # 引数を付けなかった場合はヘルプを表示して終了する
    if len(sys.argv) == 1:
        parser.parse_args(["-h"])
        sys.exit(0)
    args = parser.parse_args()

    try:
        # 管理者アカウント入力
        if args.remove_user:
            del_user = True
            admin_account = Action.generate_account("Admin")
        else:
            del_user = False
            admin_account = None

        # ユーザアカウント入力
        user_account = Action.generate_account('user')

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
            elif len(port) > 5:
                print('input port(Max 5 digits)')
            else:
                port = int(port)
                break

        # 入力値表示
        if args.remove_user and admin_account is not None:
            Action.value_output('admin', admin_account)

        Action.value_output('user', user_account)

        print(f"""
        host : {host}
        port : {port}
        """)

        # 最終確認
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
                       del_user=del_user)

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)

if __name__ == "__main__":
    main()