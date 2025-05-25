import time

import requests
import os

NOTION_TOKEN = input("Notion 통합 토큰을 입력하세요: ").strip()
DATABASE_ID = input("대상 노션 데이터베이스의 ID를 입력하세요: ").strip()

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def get_db_title(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    res = requests.get(url, headers=headers)
    data = res.json()
    try:
        title = ''.join([t['plain_text'] for t in data['title']])
    except Exception:
        title = '[제목 조회 불가]'
    return title

def get_all_page_ids(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    page_ids = []
    has_more = True
    next_cursor = None

    while has_more:
        body = {"page_size": 100}
        if next_cursor:
            body["start_cursor"] = next_cursor
        res = requests.post(url, headers=headers, json=body)
        data = res.json()
        page_ids += [result["id"] for result in data["results"]]
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)
    return page_ids

def delete_pages(page_ids):
    for i, pid in enumerate(page_ids, 1):
        url = f"https://api.notion.com/v1/pages/{pid}"
        requests.patch(url, headers=headers, json={"archived": True})
        print(f"[{i}/{len(page_ids)}] 삭제 완료: {pid}")
        time.sleep(0.35)  # Notion API rate limit 고려 (약 3 req/sec)

def restore_pages(page_ids):
    for i, pid in enumerate(page_ids, 1):
        url = f"https://api.notion.com/v1/pages/{pid}"
        requests.patch(url, headers=headers, json={"archived": False})
        print(f"[{i}/{len(page_ids)}] 복원 완료: {pid}")
        time.sleep(0.35)  # Notion API rate limit 고려 (약 3 req/sec)

def backup_page_ids(page_ids, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        for pid in page_ids:
            f.write(pid + "\n")

def load_page_ids(file_path):
    if not os.path.exists(file_path):
        print(f"파일 {file_path} 이(가) 존재하지 않습니다.")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    mode = input("작업 모드를 선택하세요 (삭제: D / 복원: R): ").strip().upper()
    db_title = get_db_title(DATABASE_ID)
    BACKUP_FILE = f"{DATABASE_ID}.txt"
    print(f"\n대상 DB명: {db_title}")

    if mode == "D":
        check = input("정말로 이 데이터베이스의 모든 행을 삭제할까요? [OK 입력시 진행] : ").strip()
        if check == "OK":
            ids = get_all_page_ids(DATABASE_ID)
            print(f"\n총 {len(ids)}개의 페이지(행)를 삭제하고, id를 '{BACKUP_FILE}'로 백업합니다!")
            backup_page_ids(ids, BACKUP_FILE)
            delete_pages(ids)
            print("삭제 및 백업 완료!")
        else:
            print("삭제가 취소되었습니다.")

    elif mode == "R":
        check = input(f"파일('{BACKUP_FILE}')에 있는 페이지 id들을 복원할까요? [OK 입력시 진행] : ").strip()
        if check == "OK":
            ids = load_page_ids(BACKUP_FILE)
            print(f"\n총 {len(ids)}개의 페이지(행)를 복원합니다!")
            restore_pages(ids)
            print("복원 완료!")
        else:
            print("복원이 취소되었습니다.")

    else:
        print("잘못된 모드입니다. 'delete' 또는 'restore' 중 하나를 입력하세요.")
