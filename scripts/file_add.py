def main():
    import sys
    import signal
    import argparse
    from edman import DB, File
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='ファイルを実験データに追加するスクリプト')
    # parser.add_argument('-c', '--collection', help='collection name.')
    parser.add_argument('objectid', help='objectid str.')
    parser.add_argument('path', help='file or Dir path.')
    # クエリは structureがembの時だけ
    parser.add_argument('-q', '--query', default=None,
                        help='Ref is ObjectId or Emb is query list strings.')
    parser.add_argument('-c', '--compress', action='store_true',
                        help='gzip compress.Default is not compressed.')
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
        file = File(db.get_db)

        # 対象oidの所属コレクションを自動的に取得 ※動作が遅い場合は使用しないこと
        collection = db.find_collection_from_objectid(args.objectid)

        # ドキュメント構造の取得
        structure = db.get_structure(collection, args.objectid)

        # クエリの変換
        query = Action.file_query_eval(args.query, structure)

        # データを作成
        files = [(file, False) for file in Action.files_read(args.path)]

        # ファイルのアップロード
        if file.upload(collection, args.objectid, tuple(files), structure,
                       query):
            print('更新しました')
        else:
            print('更新に失敗しました')

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)


if __name__ == "__main__":
    main()
