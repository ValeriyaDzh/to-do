import pytest
from httpx import AsyncClient
from tests.conftest import TEST_TASK, TEST_USER

TASK_DATA = {
    "title": "some title",
    "description": "some description",
}


@pytest.mark.anyio
async def test_create_task(api_client: AsyncClient, mock_jwt_decode):

    mock_jwt_decode.return_value = {"sub": "john_doe"}

    response = await api_client.post(
        "api/tasks", json=TASK_DATA, headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 201
    response_data = response.json()

    for key, value in TASK_DATA.items():
        assert value == response_data[key]


@pytest.mark.anyio
async def test_empty_title_exception(api_client: AsyncClient, mock_jwt_decode):
    task_data = {"title": ""}
    mock_jwt_decode.return_value = {"sub": "john_doe"}

    response = await api_client.post(
        "api/tasks", json=task_data, headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 422

    assert "Title must contains at least one simbol" in response.json()["detail"]


@pytest.mark.anyio
async def test_users_task(api_client: AsyncClient, mock_jwt_decode):
    mock_jwt_decode.return_value = {"sub": "john_doe"}

    response = await api_client.get(
        "api/tasks", headers={"Authorization": "Bearer testtoken"}
    )
    response.status_code == 200
    response_data = response.json()

    assert len(response_data) == 1
    for key, value in TASK_DATA.items():
        assert value == response_data[0][key]


@pytest.mark.anyio
async def test_edit_task(api_client: AsyncClient, mock_jwt_decode):
    mock_jwt_decode.return_value = {"sub": "test"}
    edit_data = {"title": "edit_new_test_task", "description": "edit_description"}

    response = await api_client.patch(
        f"api/task/1c9e02ef-f0b0-4336-beb5-aade2e704547",
        headers={"Authorization": "Bearer testtoken"},
        json=edit_data,
    )
    assert response.status_code == 200

    response_data = response.json()
    for key, value in edit_data.items():
        assert value == response_data[key]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "task_id, status, detail",
    [
        (
            "cb417dbc-4c34-4028-af90-64c3b79300e2",
            404,
            "Task not found",
        ),
        (
            "1c9e02ef-f0b0-4336-beb5-aade2e704547",
            403,
            "There are no permission for changes",
        ),
    ],
)
async def test_edit_task_exception(
    api_client: AsyncClient, mock_jwt_decode, task_id, status, detail
):
    mock_jwt_decode.return_value = {"sub": "john_doe"}

    response = await api_client.patch(
        f"api/task/{task_id}",
        headers={"Authorization": "Bearer testtoken"},
        json={"title": "exception"},
    )
    assert response.status_code == status

    assert detail in response.json()["detail"]


@pytest.mark.anyio
async def test_add_task_permission(api_client: AsyncClient, mock_jwt_decode):
    mock_jwt_decode.return_value = {"sub": "test"}

    data = {"user_login": "john_doe", "permission": "edit"}
    response = await api_client.post(
        f"api/task/1c9e02ef-f0b0-4336-beb5-aade2e704547/permissions",
        headers={"Authorization": "Bearer testtoken"},
        json=data,
    )

    assert response.status_code == 200
    assert data["user_login"] in response.json()["message"]
