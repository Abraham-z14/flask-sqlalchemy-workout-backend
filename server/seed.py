#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise


with app.app_context():
    print("Clearing database...")

    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    db.session.commit()

    print("Creating exercises...")

    push_up = Exercise(
        name="Push-Up",
        category="Strength",
        equipment_needed=False,
    )

    squat = Exercise(
        name="Goblet Squat",
        category="Strength",
        equipment_needed=True,
    )

    plank = Exercise(
        name="Plank",
        category="Core",
        equipment_needed=False,
    )

    pull_up = Exercise(
        name="Pull-Up",
        category="Strength",
        equipment_needed=True,
    )

    exercises = [
        push_up,
        squat,
        plank,
        pull_up,
    ]

    db.session.add_all(exercises)
    db.session.commit()

    print("Creating workouts...")

    workout_one = Workout(
        date=date(2026, 11, 20),
        duration_minutes=35,
        notes="Full-body strength workout.",
    )

    workout_two = Workout(
        date=date(2026, 11, 21),
        duration_minutes=25,
        notes="Upper-body and core session.",
    )

    workouts = [
        workout_one,
        workout_two,
    ]

    db.session.add_all(workouts)
    db.session.commit()

    print("Connecting exercises to workouts...")

    workout_exercises = [
        WorkoutExercise(
            workout=workout_one,
            exercise=push_up,
            sets=3,
            reps=12,
        ),
        WorkoutExercise(
            workout=workout_one,
            exercise=squat,
            sets=3,
            reps=10,
        ),
        WorkoutExercise(
            workout=workout_one,
            exercise=plank,
            sets=3,
            duration_seconds=45,
        ),
        WorkoutExercise(
            workout=workout_two,
            exercise=pull_up,
            sets=3,
            reps=6,
        ),
        WorkoutExercise(
            workout=workout_two,
            exercise=plank,
            sets=3,
            duration_seconds=60,
        ),
    ]

    db.session.add_all(workout_exercises)
    db.session.commit()

    print("Database seeded successfully.")