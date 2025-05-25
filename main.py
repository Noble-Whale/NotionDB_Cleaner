import requests

NOTION_TOKEN = input("Notion 통합 토큰을 입력하세요: ").strip()
DATABASE_ID = input("삭제할 노션 데이터베이스의 ID를 입력하세요: ").strip()

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def get_db_title(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    res = requests.get(url, headers=headers)
    data = res.json()
    # DB명 추출 (DB 커버, 아이콘 등 복잡할 수 있으니 try-except로)
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

if __name__ == "__main__":
    db_title = get_db_title(DATABASE_ID)
    print(f"\n삭제하려는 DB명: {db_title}")
    check = input("정말로 이 데이터베이스의 모든 행을 삭제할까요? [OK 입력시 진행] : ").strip()
    if check == "OK":
        ids = get_all_page_ids(DATABASE_ID)
        print(f"\n총 {len(ids)}개의 페이지(행)를 삭제합니다!")
        delete_pages(ids)
        print("삭제 완료!")
    else:
        print("삭제가 취소되었습니다.")
