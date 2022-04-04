def main():
    import sys
    import signal
    import argparse
    from pathlib import Path
    from edman import DB, JsonManager
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='DB内のRefドキュメントに型を適応するスクリプト')
    parser.add_argument('path', help='JSON file path.')
    parser.add_argument('-l', '--logfile',
                        help='Output logfile path. default is current dir.')
    parser.add_argument('-n', '--no_logfile', help='Do not output log file.',
                        action='store_true')
    parser.add_argument('-i', '--inifile', help='DB connect file path.')

    # 引数を付けなかった場合はヘルプを表示して終了する
    if len(sys.argv) == 1:
        parser.parse_args(["-h"])
        sys.exit(0)
    args = parser.parse_args()

    # 結果を記録する場合はパスの存在を調べる
    log_p = Path(args.logfile) if args.logfile is not None else Path.cwd()
    if not log_p.exists() or not log_p.is_dir():
        sys.exit('指定のログファイル用ディレクトリパスが不正です')

    # JSONのパスを取得
    p = Path(args.path)
    if not p.exists() or not p.is_file() or p.suffix != '.json':
        sys.exit('指定のJSONファイルがありません')

    try:
        # 接続用iniファイル読み込み
        con = Action.reading_config_file(args.inifile)
        db = DB(con)
        process_data = {}

        # ファイル読み込み、実行
        # ファイル単体の場合でもジェネレータなのでループを使用する
        for i in Action.file_gen((p,)):
            process_data = db.bson_type(i)

        # ログファイル書き出し処理
        if not args.no_logfile:
            jm = JsonManager()
            jm.save(process_data, log_p, name='type_assigned_log', date=True)

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)

if __name__ == "__main__":
    main()