def main():
    import sys
    import signal
    import argparse
    from edman import DB
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='ドキュメントを削除するスクリプト')
    # parser.add_argument('-c', '--collection', help='collection name.')
    parser.add_argument('objectid', help='objectid str.')
    parser.add_argument('-i', '--inifile', help='DB connect file path.')

    # 引数を付けなかった場合はヘルプを表示して終了する
    if len(sys.argv) == 1:
        parser.parse_args(["-h"])
        sys.exit(0)
    args = parser.parse_args()

    try:
        # iniファイル読み込み
        con = Action.reading_config_file(args.inifile)

        db = DB(con)
        # 対象oidの所属コレクションを自動的に取得 ※動作が遅い場合は使用しないこと
        collection = db.find_collection_from_objectid(args.objectid)

        # 指定のドキュメントの文書構造を取得
        structure = db.get_structure(collection, args.objectid)

        # 削除処理
        if db.delete(args.objectid, collection, structure):
            print('削除成功')
        else:
            print('削除失敗')

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)

if __name__ == "__main__":
    main()