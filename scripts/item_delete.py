def main():

    import sys
    import signal
    import argparse
    from edman import DB
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='ドキュメントの項目を削除するスクリプト')
    # parser.add_argument('-c', '--collection', help='collection name.')
    parser.add_argument('objectid', help='objectid str.')
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

        # 対象oidの所属コレクションを自動的に取得 ※動作が遅い場合は使用しないこと
        collection = db.find_collection_from_objectid(args.objectid)

        # ドキュメント構造の取得
        structure = db.get_structure(collection, args.objectid)

        # クエリの変換
        query = Action.file_query_eval(args.query, structure)

        # ドキュメント取得
        doc = db.doc(collection, args.objectid, query)
        doc_keys = list(doc.keys())

        # 項目を画面表示
        for idx, (key, value) in enumerate(doc.items()):
            print('(' + str(idx) + ')', key, ':', value)

        # 表示されている選択番号を入力
        if len(doc) > 0:
            while True:
                selected_idx = input('0 - ' + str(len(doc) - 1) + ' > ')
                if selected_idx.isdecimal() and (
                        0 <= int(selected_idx) < len(doc)):
                    break
                else:
                    print('Required!')
        else:
            sys.exit('ドキュメントが取得できていません')

        # 削除処理
        if db.item_delete(collection, args.objectid,
                          doc_keys[int(selected_idx)], query):
            print('削除成功')
        else:
            print('削除失敗')

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)

if __name__ == "__main__":
    main()