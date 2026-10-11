import sqlite3
import google.generativeai as genai
import os

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

def add_task(task_name: str, deadline: str = "未設定") -> str:
    """
    新しいタスクをデータベースに追加します。
    Args:
        task_name: タスクの内容
        deadline: 期限（指定がない場合は"未設定"）
    """
    cursor.execute("INSERT INTO tasks (task_name, deadline) VALUES (?, ?)", (task_name, deadline))
    conn.commit()
    return f"システム報告: タスク「{task_name}」(期限: {deadline}) をDBに保存しました。"

def get_active_tasks() -> str:
    """
    現在登録されている未完了のタスク一覧をデータベースから取得します。
    ユーザーに「今のタスクは？」と聞かれたらこれを使ってください。
    """
    cursor.execute("SELECT * FROM tasks WHERE status = 0")
    tasks = cursor.fetchall()
    
    if not tasks:
        return "システム報告: 現在、未完了のタスクはありません。"
    
    result_text = "システム報告: 以下の未完了タスクが見つかりました。\n"
    for task in tasks:
        deadline_text = task[2] if task[2] else "設定なし"
        result_text += f"- ID:{task[0]} 「{task[1]}」 (期限: {deadline_text})\n"
    return result_text

def complete_task(task_id: int) -> str:
    """
    指定されたIDのタスクを完了（ステータスを1）にします。
    Args:
        task_id: 完了にしたいタスクのID（数値）
    """
    cursor.execute("UPDATE tasks SET status = 1 WHERE id = ?", (task_id,))
    conn.commit()
    return f"システム報告: ID {task_id} のタスクを完了としてDBを更新しました。"

# 3. Gemini APIの設定と連携
# APIキーの設定（環境変数から取得、または直接文字列で入力）
genai.configure(api_key="(ここにAPIキーを入力)")

# AIに自作関数（tools）を渡してモデルを初期化
model = genai.GenerativeModel(
    model_name='gemini-3.8-flash',
    tools=[add_task, get_active_tasks, complete_task]
)

# 自動関数呼び出しを有効にしてチャットを開始
chat = model.start_chat(enable_automatic_function_calling=True)

# 4. メインの対話ループ
print("========================================")
print("AIアシスタント起動")
print("========================================")
print("「牛乳買うのメモして」「今のタスク教えて」「ID 1番を完了にして」など話しかけてください。\n")

while True:
    user_input = input("あなた: ")
    if user_input.strip() == "終了":
        print("AI: お疲れ様でした。システムを終了します。")
        break
    if not user_input.strip():
        continue

    # AIにメッセージを送信（必要に応じてAIが自動で関数を呼び出します）
    try:
        response = chat.send_message(user_input)
        print(f"AI: {response.text}\n")
    except Exception as e:
        print(f"!! エラーが発生しました: {e}\n !!")

conn.close()