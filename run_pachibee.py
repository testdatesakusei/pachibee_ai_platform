# -*- coding: utf-8 -*-
"""
AI Intelligence Launcher v2
"""

from pathlib import Path
import subprocess
import sys
import webbrowser
import time

ROOT = Path(__file__).resolve().parent

MENU = {
    "1": ("ベースExcel取込", "02_import/import_base_excel.py"),
    "2": ("週次データ作成", "02_import/prepare_weekly_performance_import.py"),
    "3": ("機種マスター作成", "02_import/create_machine_master.py"),
    "4": ("Feature Snapshot作成", "04_ai_analysis/build_machine_feature_snapshot.py"),
    "5": ("Machine Intelligence v2", "04_ai_analysis/machine_intelligence_engine_v2.py"),
    "6": ("市場データテンプレート作成", "02_import/create_market_data_template.py"),
}


def run_script(script_path):
    path = ROOT / script_path

    if not path.exists():
        print(f"\nファイルがありません:\n{path}\n")
        return

    print("\n===================================")
    print(f"実行: {script_path}")
    print("===================================\n")

    result = subprocess.run([sys.executable, str(path)])

    if result.returncode == 0:
        print("\n完了しました。")
    else:
        print("\nエラーが発生しました。")


def start_web():
    web_dir = ROOT / "06_web"
    app_path = web_dir / "app.py"

    if not app_path.exists():
        print(f"\napp.py が見つかりません:\n{app_path}\n")
        return

    print("\n===================================")
    print("Web Dashboard 起動")
    print("===================================")
    print("ブラウザで http://127.0.0.1:5000 を開きます。")
    print("終了するときは、この画面で Ctrl + C を押してください。\n")

    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000")

    subprocess.run([sys.executable, str(app_path)], cwd=str(web_dir))


while True:
    print("\n")
    print("=" * 45)
    print("        AI Intelligence Platform")
    print("=" * 45)
    print("1 ベースExcel取込")
    print("2 週次データCSV作成")
    print("3 機種マスター作成")
    print("4 Feature Snapshot作成")
    print("5 Machine Intelligence v2")
    print("6 市場データテンプレート作成")
    print("7 Web Dashboard起動")
    print("0 終了")
    print("=" * 45)

    cmd = input("番号を入力してください：").strip()

    if cmd == "0":
        break

    if cmd == "7":
        start_web()
        continue

    if cmd not in MENU:
        print("番号が違います。")
        continue

    run_script(MENU[cmd][1])
    input("\nEnterキーでメニューへ戻ります...")