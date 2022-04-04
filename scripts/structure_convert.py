def main():

    import sys
    import signal
    import argparse
    from edman import DB
    from scripts.action import Action

    # Ctrl-Cを押下された時の対策
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit('\n'))

    # コマンドライン引数処理
    parser = argparse.ArgumentParser(description='DBから検索したデータをコンバートしてDBに入れるスクリプト')
    # parser.add_argument('-c', '--collection', help='collection name.')
    parser.add_argument('objectid', help='objectid str.')
    # parser.add_argument('-s', '--structure', default='ref',
    #                     help='Select ref(Reference, default) or emb(embedded).')
    parser.add_argument('new_collection', help='new collection name.')
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

        # 対象のドキュメントがrefかembかを調べる
        # (ただし、子要素が存在しないドキュメントの場合は必ずembと表示される)
        current_structure = db.get_structure(collection, args.objectid)
        print(f'このドキュメントは {current_structure} 形式です')
        structures = ['emb', 'ref']
        structures.remove(current_structure)

        while True:
            convert_selected = input(f'{structures[0]}に変更しますか？ y/n(exit) >> ')
            if convert_selected == 'y':
                result = db.structure(collection, args.objectid, structures[0],
                                      args.new_collection)
                print('\n', result)
                break
            elif convert_selected == 'n':
                sys.exit()
            else:
                continue

    except Exception as e:
        tb = sys.exc_info()[2]
        sys.stderr.write(f'{type(e).__name__}: {e.with_traceback(tb)}\n')
        sys.exit(1)

if __name__ == "__main__":
    main()