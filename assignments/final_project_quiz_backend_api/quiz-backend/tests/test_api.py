def _create_question(client, text="Sample question?", category="General Knowledge"):
    resp = client.post("/questions", json={"question_text": text, "category": category})
    assert resp.status_code == 201, resp.text
    return resp.json()


# root and health endpoints

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_root(client):
    assert client.get("/").status_code == 200


# question endpoints

def test_create_and_get_question(client):
    q = _create_question(client)
    assert q["id"] > 0
    assert q["question_text"] == "Sample question?"
    assert q["category"] == "General Knowledge"
    assert q["choices"] == []

    got = client.get(f"/questions/{q['id']}")
    assert got.status_code == 200
    assert got.json()["id"] == q["id"]


def test_list_questions_and_category_filter(client):
    _create_question(client, "Q1?", "Programming")
    _create_question(client, "Q2?", "Mathematics")

    all_questions = client.get("/questions").json()
    assert len(all_questions) == 2

    programming = client.get("/questions", params={"category": "Programming"}).json()
    assert len(programming) == 1
    assert programming[0]["category"] == "Programming"


def test_update_question(client):
    q = _create_question(client)
    resp = client.put(
        f"/questions/{q['id']}",
        json={"question_text": "Updated?", "category": "Data Science"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["question_text"] == "Updated?"
    assert body["category"] == "Data Science"


def test_get_missing_question_returns_404(client):
    assert client.get("/questions/99999").status_code == 404


def test_delete_question_cascades_to_choices(client):
    q = _create_question(client)
    c1 = client.post("/choices", json={"choice_text": "A", "is_correct": True, "question_id": q["id"]}).json()
    c2 = client.post("/choices", json={"choice_text": "B", "is_correct": False, "question_id": q["id"]}).json()

    got = client.get(f"/questions/{q['id']}").json()
    assert len(got["choices"]) == 2

    assert client.delete(f"/questions/{q['id']}").status_code == 204
    assert client.get(f"/questions/{q['id']}").status_code == 404
    # choices should be deleted along with the question
    assert client.get(f"/choices/{c1['id']}").status_code == 404
    assert client.get(f"/choices/{c2['id']}").status_code == 404


# choice endpoints

def test_choice_full_lifecycle(client):
    q = _create_question(client)

    created = client.post(
        "/choices",
        json={"choice_text": "Yes", "is_correct": True, "question_id": q["id"]},
    )
    assert created.status_code == 201
    choice = created.json()
    assert choice["question_id"] == q["id"]
    assert choice["is_correct"] is True

    listed = client.get("/choices", params={"question_id": q["id"]}).json()
    assert len(listed) == 1

    updated = client.put(
        f"/choices/{choice['id']}",
        json={"choice_text": "Maybe", "is_correct": False},
    )
    assert updated.status_code == 200
    assert updated.json()["choice_text"] == "Maybe"
    assert updated.json()["is_correct"] is False

    assert client.delete(f"/choices/{choice['id']}").status_code == 204
    assert client.get(f"/choices/{choice['id']}").status_code == 404


def test_create_choice_for_missing_question_returns_404(client):
    resp = client.post("/choices", json={"choice_text": "X", "is_correct": False, "question_id": 99999})
    assert resp.status_code == 404


# validation

def test_empty_question_text_rejected(client):
    assert client.post("/questions", json={"question_text": ""}).status_code == 422


def test_unknown_field_rejected(client):
    resp = client.post("/questions", json={"question_text": "ok", "surprise": "field"})
    assert resp.status_code == 422
