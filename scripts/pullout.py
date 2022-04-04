def main():
    import sys
    import signal
    import argparse
    from edman import DB
    # from edman import DB, JsonManager
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(
        description='特定コレクション内のembデータの特定のキーに対してref化を行うスクリプト')
    parser.add_argument('collection')
    parser.add_argument('pullout_key')
    parser.add_argument('-e', '--exclusion_keys', nargs='*')
    parser.add_argument('-i', '--inifile', help='DB connect file path.')
    # parser.add_argument('-d', '--dir',
    #                     help='Dir of report files.',
    #                     default=None)

    # 引数を付けなかった場合はヘルプを表示して終了する
    if len(sys.argv) == 1:
        parser.parse_args(["-h"])
        sys.exit(0)
    args = parser.parse_args()

    # 結果を記録する場合はパスの存在を調べる
    # if args.dir is not None:
    #     p = Path(args.dir)
    #     if not p.exists() and not p.is_dir():
    #         sys.exit('パスが不正です')

    try:
        # iniファイル読み込み
        con = Action.reading_config_file(args.inifile)

        db = DB(con)
        exclusion = tuple(args.exclusion_keys if args.exclusion_keys is not None else [])
        result = db.loop_exclusion_key_and_ref(args.collection, args.pullout_key, exclusion)

        # 結果を保存する
        # if args.dir is not None:
        #     jm = JsonManager()
        #     jm.save(result, args.dir, 'pullout', date=True)

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)

if __name__ == "__main__":
    main()