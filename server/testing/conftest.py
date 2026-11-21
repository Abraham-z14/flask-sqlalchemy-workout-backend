from datetime import date

import pytest

from app import app
from models import db, Exercise, Workout, WorkoutExercise


@pytest.fixture()
def seeded_database():
    """Reset the database and provide predictable records for each test."""

    app.config["TESTING"] = True

    with app.app_context():
        db.session.rollback()

        WorkoutExercise.query.delete()
        Workout.query.delete()
        Exercise.query.delete()
        db.session.commit()

        push_up = Exercise(
            name="Push-Up",
            category="Strength",
            equipment_needed=False,
        )

        plank = Exercise(
            name="Plank",
            category="Core",
            equipment_needed=False,
        )

        workout = Workout(
            date=date(2026, 11, 21),
            duration_minutes=30,
            notes="Test workout.",
        )

        db.session.add_all([
            push_up,
            plank,
            workout,
        ])
        db.session.commit()

        workout_exercise = WorkoutExercise(
            workout=workout,
            exercise=push_up,
            sets=3,
            reps=10,
        )

        db.session.add(workout_exercise)
        db.session.commit()

        data = {
            "workout_id": workout.id,
            "push_up_id": push_up.id,
            "plank_id": plank.id,
            "workout_exercise_id": workout_exercise.id,
        }

        yield data

        db.session.rollback()

        WorkoutExercise.query.delete()
        Workout.query.delete()
        Exercise.query.delete()
        db.session.commit()


@pytest.fixture()
def client(seeded_database):
    """Provide a Flask test client backed by a fresh database."""

    return app.test_client()