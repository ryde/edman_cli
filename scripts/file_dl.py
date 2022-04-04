def main():

    import sys
    import signal
    import argparse
    from edman import DB, File
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(
        description='ファイルを実験データからダウンロードするスクリプト')
    # parser.add_argument('-c', '--collection', help='collection name.')
    parser.add_argument('objectid', help='objectid str.')
    parser.add_argument('path', help='Download Dir path.')
    # クエリは structureがembの時だけ
    parser.add_argument('-q', '--query', default=None,
                        help='Ref is ObjectId or Emb is query list strings.')
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

        # ファイル名一覧を取得
        file_names = file.get_file_names(collection, args.objectid, structure,
                                         query)
        if not file_names:
            sys.exit('ファイルは存在しません')

        file_oids = []
        # ファイル名一覧を画面表示&file_oid用リスト作成
        for idx, (oid, filename) in enumerate(file_names.items()):
            print('(' + str(idx) + ')', filename, oid)
            file_oids.append(oid)

        # 複数ファイルの場合、表示されている選択番号を入力
        if len(file_names) > 1:
            while True:
                selected_idx = input('0 - ' + str(len(file_names) - 1) + ' > ')
                if selected_idx.isdecimal() and (
                        0 <= int(selected_idx) < len(file_names)):
                    break
                else:
                    print('Required!')
        # ファイルが一つしかない場合は選択無しでDL
        elif len(file_names) == 1:
            selected_idx = 0
        else:
            sys.exit('インデックスが不正です')

        # 指定のディレクトリにダウンロード
        if file.download(file_oids[int(selected_idx)], args.path):
            print('DLしました')

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)

if __name__ == "__main__":
    main()