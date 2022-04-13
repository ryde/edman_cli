edman_cli
=========

|py_version|

|  EDMAN(KEK IMSS SBRC/PF Experimental Data Management System)用のコマンドラインスクリプト。
|  コマンドとしてインストールされます。

Requirement
-----------
-   pymongo
-   python-dateutil
-   jmespath


Scripts Usage
-------------
コマンドとしてインストールされます

|  ◯スクリプトで使用するクエリについて
|
|  検索用クエリ
|    検索の際はMongoDB(pymongo)のフィルタ形式で指定します
|    クエリ形式は "{フィルタ条件}"
|      MongoDB参照:  https://www.mongodb.com/docs/manual/reference/method/db.collection.find/
|      pymongoのfind参照:  https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html
|
|  階層指定クエリ
|    emb(Embedded)形式でデータが入っている場合は下記のようなクエリで指定します
|    構造上、embの時はクエリを使用しなければデータに到達できません
|    例:

::

       {
           "collectionA":[
               {
                   "collectionB":{"data1":"value1"}
               },
               {
                   "collectionC:{
                       "data2":"value2",
                       "CollectionD":{
                           "data3":"value3",
                           "data4":"value4"
                       }
                   }
               }
           ]
       }

|   ・data4を消したい場合
|       "['collectionA', '1', 'collectionC', 'collectionD']"
|   リストで消したい項目の直近の親までを指定する
|   データが複数あり、リストで囲まれていた場合は添字を数字で指定
|
|  ◯各コマンド
|  ed_entry: jsonファイルからMongoDBに投入
|  ed_find: データを検索し、jsonに保存 検索用クエリを使用します
|  ed_item_delete: データ内の項目を消す embの時、階層指定クエリを使用します
|  ed_update: データの更新(更新用jsonファイルを用意)
|  ed_delete: ドキュメントの削除(embは全削除、refは指定したobjectid以下を削除)
|  ed_file_add:  該当データにファイルを添付する embの時、階層指定クエリを使用します
|  ed_file_dl: 添付ファイルをダウンロード embの時、階層指定クエリを使用します
|  ed_file_delete: 添付ファイルを削除 embの時、階層指定クエリを使用します
|  ed_db_create: データベース及びユーザ作成操作支援用(MongoDBの管理者アカウントが必要)
|  ed_db_destroy: データベース削除操作支援用(ユーザ削除はソース書き換えが必要)
|  ed_structure_convert: DB内のembをrefへ変換、またはその逆を行います
|  ed_pullout: コレクション内のembのキーを指定し、そのキーを含む階層を全てrefに変換します
|  ed_assign_bson_type: DB内のRefドキュメントに型を適応します

オプションなど詳しくは::

  command_name -h

Install
-------

pip install::

 pip install edman

Licence
-------
MIT

Author
------

[ryde](https://github.com/ryde)

.. |py_version| image:: https://img.shields.io/badge/python-3.9-blue.svg
    :alt: Use python
