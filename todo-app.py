import sqlite3

#データベースへの接続
conn = sqlite3.connect('todo.db')
cursor = conn.cursor()

#テーブル（表）の作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    deadline TEXT,
    status INTEGER DEFAULT 0
)
''')
conn.commit()

# --- 機能の定義 ---

def add_task(task_name, deadline):
    # ? を使うことで、セキュリティリスク（SQLインジェクション）を防ぐ
    cursor.execute("INSERT INTO tasks (task_name, deadline) VALUES (?, ?)", (task_name, deadline))
    conn.commit()
    print(f"追加しました: {task_name} (期限: {deadline})")

def show_active_tasks():
    # WHERE status = 0 を指定して、未完了だけを取得
    cursor.execute("SELECT * FROM tasks WHERE status = 0")
    tasks = cursor.fetchall()
    
    print("\n--- 未完了のTODOリスト ---")
    if not tasks:
        print("未完了のタスクはありません！")
    else:
        for task in tasks:
            deadline_text = task[2] if task[2] else "設定なし"
            print(f"[{task[0]}] {task[1]} (期限: {deadline_text})")
    print("------------------------\n")

def complete_task(task_id):
    # 指定されたIDのステータスを「1（完了）」に上書き更新
    cursor.execute("UPDATE tasks SET status = 1 WHERE id = ?", (task_id,))
    conn.commit()
    print(f"ID {task_id} を完了にしました！お疲れ様です！")

def show_completed_tasks():
    # status = 1（完了）のデータだけを取得します
    cursor.execute("SELECT * FROM tasks WHERE status = 1")
    tasks = cursor.fetchall()
    
    print("\n--- 完了済みのTODO履歴 ---")
    if not tasks:
        print("完了済みのタスクはまだありません。")
    else:
        for task in tasks:
            deadline_text = task[2] if task[2] else "設定なし"
            print(f"[{task[0]}] {task[1]} (期限: {deadline_text})")
    print("------------------------\n")

def search_tasks(keyword):
    # 「%」は「前後にどんな文字があってもOK」という意味の記号
    search_term = f"%{keyword}%"
    
    cursor.execute(
        "SELECT * FROM tasks WHERE task_name LIKE ? OR deadline LIKE ?", 
        (search_term, search_term)
    )
    
    tasks = cursor.fetchall()
    
    print(f"\n--- 「{keyword}」の検索結果 ---")
    if not tasks:
        print("見つかりませんでした。")
    else:
        for task in tasks:
            deadline_text = task[2] if task[2] else "設定なし"
            print(f"[{task[0]}] {task[1]} (期限: {deadline_text})")
    print("------------------------\n")

def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    print(f"ID {task_id} のタスクを削除しました。")

def update_task(task_id, new_name, new_deadline):
    cursor.execute("UPDATE tasks SET task_name = ?, deadline = ? WHERE id = ?", (new_name, new_deadline, task_id))
    conn.commit()
    print(f"✅ ID {task_id} のタスクを更新しました。")

# --- メインの操作ループ ---

print("=== シンプルTODOアプリ ===")
while True:
    print("操作を選んでください: 1(追加), 2(未完了を表示), 3(タスクを完了にする)", \
                                "4(更新), 5(削除), 6(検索), 7(完了済みタスクを表示), 0(終了)")
    choice = input("> ")

    if choice == '1':
        new_task = input("新しいタスクを入力: ")
        new_deadline = input("期限を入力: ")
        if new_task.strip():
            add_task(new_task, new_deadline)
            
    elif choice == '2':
        show_active_tasks()
        
    elif choice == '3':
        show_active_tasks()
        target_id = input("完了にしたタスクのIDを入力: ")
        complete_task(target_id)

    elif choice == '4':
        show_tasks()
        target_id = input("更新したいタスクのIDを入力: ")
        new_name = input("新しいタスク名を入力: ")
        new_deadline = input("新しい期限を入力: ")
        update_task(target_id, new_name, new_deadline)

    elif choice == '5':
        show_tasks()
        target_id = input("削除したいタスクのIDを入力: ")
        delete_task(target_id)

    elif choice == '6':
        keyword = input("検索したいキーワードを入力: ")
        if keyword.strip():
            search_tasks(keyword)

    elif choice=="7":
        show_completed_tasks()

    elif choice == '0':
        print("終了します。")
        break

    else:
        print("!! 正しい番号を入力してください !!")

# アプリ終了時にデータベース接続を閉じる
conn.close()