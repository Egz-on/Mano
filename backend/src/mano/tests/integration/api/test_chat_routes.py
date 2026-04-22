from uuid import UUID


async def test_create_conversation_requires_auth(async_client) -> None:
    response = await async_client.post("/api/v1/conversations/")

    assert response.status_code == 401


async def test_create_conversation_and_list_messages(async_client, auth_header_client) -> None:
    create_response = await async_client.post("/api/v1/conversations/", headers=auth_header_client)

    assert create_response.status_code == 201
    conversation = create_response.json()
    conversation_id = conversation["id"]
    assert UUID(conversation_id)

    get_response = await async_client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_header_client,
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == conversation_id

    messages_response = await async_client.get(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers=auth_header_client,
    )
    assert messages_response.status_code == 200
    assert messages_response.json() == []


async def test_create_message_persists_in_conversation(async_client, auth_header_client) -> None:
    create_response = await async_client.post("/api/v1/conversations/", headers=auth_header_client)
    conversation_id = create_response.json()["id"]

    message_response = await async_client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "  Hello realtime world  "},
        headers=auth_header_client,
    )

    assert message_response.status_code == 201
    message = message_response.json()
    assert message["conversation_id"] == conversation_id
    assert message["content"] == "Hello realtime world"

    messages_response = await async_client.get(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers=auth_header_client,
    )
    assert messages_response.status_code == 200
    messages = messages_response.json()
    assert len(messages) == 1
    assert messages[0]["id"] == message["id"]
