def main():

    import sys
    import signal
    import argparse
    from pathlib import Path
    from edman import DB, Convert, JsonManager
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='JSONからDBに投入するスクリプト')
    parser.add_argument('path', help='file or Dir path.')
    parser.add_argument('-rd', '--result_dir',
                        help='Dir of report files. default is current dir.',
                        default=None)
    parser.add_argument('-s', '--structure', default='ref',
                        help='Select ref(Reference, default) or emb(embedded).')
    parser.add_argument('-i', '--inifile', help='DB connect file path.')

    # 引数を付けなかった場合はヘルプを表示して終了する
    if len(sys.argv) == 1:
        parser.parse_args(["-h"])
        sys.exit(0)
    args = parser.parse_args()

    # 構造はrefかembのどちらか ※モジュール内でも判断できる
    if not (args.structure == 'ref' or args.structure == 'emb'):
        parser.error("--structure requires 'ref' or 'emb'.")

    # 結果を記録する場合はパスの存在を調べる
    if args.result_dir is not None:
        p = Path(args.result_dir)
        if not p.exists() and not p.is_dir():
            sys.exit('パスが不正です')

    try:
        # iniファイル読み込み
        con = Action.reading_config_file(args.inifile)

        db = DB(con)
        jm = JsonManager()
        convert = Convert()
        json_files = Action.files_read(args.path, 'json')

        for file in Action.file_gen(json_files):
            # Edman用にjsonをコンバート
            converted_edman = convert.dict_to_edman(file, mode=args.structure)
            # コンバート結果を保存する場合
            # jm.save({'converted_edman': converted_edman}, args.result_dir,
            #         name='edman_json_list', date=True)

            # DBへインサート
            inserted_report = db.insert(converted_edman)

            if args.result_dir is not None:
                jm.save({'inserted_report': inserted_report}, args.result_dir,
                        name='inserted', date=True)

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)

if __name__ == "__main__":
    main()