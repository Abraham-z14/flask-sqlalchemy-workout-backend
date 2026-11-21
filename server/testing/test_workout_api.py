from app import app
from models import WorkoutExercise


def test_get_workouts_returns_workout_relationship_data(
    client,
    seeded_database,
):
    response = client.get("/workouts")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 1

    workout = data[0]

    assert workout["id"] == seeded_database["workout_id"]
    assert workout["duration_minutes"] == 30
    assert workout["notes"] == "Test workout."

    assert len(workout["exercises"]) == 1
    assert workout["exercises"][0]["name"] == "Push-Up"

    assert len(workout["workout_exercises"]) == 1
    assert workout["workout_exercises"][0]["sets"] == 3
    assert workout["workout_exercises"][0]["reps"] == 10


def test_get_single_workout_and_missing_workout(
    client,
    seeded_database,
):
    workout_id = seeded_database["workout_id"]

    response = client.get(f"/workouts/{workout_id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == workout_id

    missing_response = client.get("/workouts/999999")

    assert missing_response.status_code == 404


def test_get_exercises_returns_associated_workouts(
    client,
    seeded_database,
):
    response = client.get("/exercises")

    assert response.status_code == 200

    exercises = response.get_json()

    assert len(exercises) == 2

    push_up = next(
        exercise
        for exercise in exercises
        if exercise["name"] == "Push-Up"
    )

    assert len(push_up["workouts"]) == 1
    assert (
        push_up["workouts"][0]["id"]
        == seeded_database["workout_id"]
    )


def test_create_exercise_and_reject_invalid_name(client):
    valid_response = client.post(
        "/exercises",
        json={
            "name": "Resistance Band Row",
            "category": "Strength",
            "equipment_needed": True,
        },
    )

    assert valid_response.status_code == 201

    valid_data = valid_response.get_json()

    assert valid_data["name"] == "Resistance Band Row"
    assert valid_data["category"] == "Strength"
    assert valid_data["equipment_needed"] is True

    invalid_response = client.post(
        "/exercises",
        json={
            "name": "   ",
            "category": "Strength",
            "equipment_needed": False,
        },
    )

    assert invalid_response.status_code == 400


def test_duplicate_exercise_name_is_rejected(client):
    payload = {
        "name": "Cable Row",
        "category": "Strength",
        "equipment_needed": True,
    }

    first_response = client.post(
        "/exercises",
        json=payload,
    )

    duplicate_response = client.post(
        "/exercises",
        json=payload,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 400


def test_create_workout_and_reject_invalid_duration(client):
    valid_response = client.post(
        "/workouts",
        json={
            "date": "2026-11-22",
            "duration_minutes": 45,
            "notes": "API test workout.",
        },
    )

    assert valid_response.status_code == 201

    workout = valid_response.get_json()

    assert workout["date"] == "2026-11-22"
    assert workout["duration_minutes"] == 45

    invalid_response = client.post(
        "/workouts",
        json={
            "date": "2026-11-22",
            "duration_minutes": 0,
        },
    )

    assert invalid_response.status_code == 400


def test_add_exercise_to_workout_and_prevent_duplicate(
    client,
    seeded_database,
):
    workout_id = seeded_database["workout_id"]
    exercise_id = seeded_database["plank_id"]

    endpoint = (
        f"/workouts/{workout_id}"
        f"/exercises/{exercise_id}"
        "/workout_exercises"
    )

    response = client.post(
        endpoint,
        json={
            "sets": 3,
            "duration_seconds": 60,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["workout_id"] == workout_id
    assert data["exercise_id"] == exercise_id
    assert data["sets"] == 3
    assert data["duration_seconds"] == 60

    duplicate_response = client.post(
        endpoint,
        json={
            "sets": 3,
            "duration_seconds": 60,
        },
    )

    assert duplicate_response.status_code == 400


def test_workout_exercise_values_must_be_positive(
    client,
    seeded_database,
):
    workout_id = seeded_database["workout_id"]
    exercise_id = seeded_database["plank_id"]

    response = client.post(
        (
            f"/workouts/{workout_id}"
            f"/exercises/{exercise_id}"
            "/workout_exercises"
        ),
        json={
            "sets": 3,
            "reps": 0,
        },
    )

    assert response.status_code == 400


def test_delete_workout_removes_associated_join_records(
    client,
    seeded_database,
):
    workout_id = seeded_database["workout_id"]

    with app.app_context():
        assert (
            WorkoutExercise.query.filter_by(
                workout_id=workout_id
            ).count()
            == 1
        )

    response = client.delete(
        f"/workouts/{workout_id}"
    )

    assert response.status_code == 200

    with app.app_context():
        assert (
            WorkoutExercise.query.filter_by(
                workout_id=workout_id
            ).count()
            == 0
        )

    assert (
        client.get(
            f"/workouts/{workout_id}"
        ).status_code
        == 404
    )


def test_delete_exercise_removes_associated_join_records(
    client,
    seeded_database,
):
    exercise_id = seeded_database["push_up_id"]

    with app.app_context():
        assert (
            WorkoutExercise.query.filter_by(
                exercise_id=exercise_id
            ).count()
            == 1
        )

    response = client.delete(
        f"/exercises/{exercise_id}"
    )

    assert response.status_code == 200

    with app.app_context():
        assert (
            WorkoutExercise.query.filter_by(
                exercise_id=exercise_id
            ).count()
            == 0
        )

    assert (
        client.get(
            f"/exercises/{exercise_id}"
        ).status_code
        == 404
    )