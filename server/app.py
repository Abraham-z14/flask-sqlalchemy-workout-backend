from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import (
    db,
    Exercise,
    Workout,
    WorkoutExercise,
)
from schemas import (
    ExerciseSchema,
    WorkoutSchema,
    WorkoutExerciseSchema,
)


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)

db.init_app(app)


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()


@app.route("/")
def index():
    return make_response(
        {"message": "Workout API"},
        200,
    )


# -------------------------
# Workout endpoints
# -------------------------


@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.order_by(
        Workout.id
    ).all()

    return make_response(
        workouts_schema.dump(workouts),
        200,
    )


@app.route("/workouts/<int:workout_id>", methods=["GET"])
def get_workout(workout_id):
    workout = db.session.get(
        Workout,
        workout_id,
    )

    if workout is None:
        return make_response(
            {"error": "Workout not found"},
            404,
        )

    return make_response(
        workout_schema.dump(workout),
        200,
    )


@app.route("/workouts", methods=["POST"])
def create_workout():
    try:
        data = workout_schema.load(
            request.get_json() or {}
        )

        workout = Workout(**data)

        db.session.add(workout)
        db.session.commit()

        return make_response(
            workout_schema.dump(workout),
            201,
        )

    except ValidationError as error:
        return make_response(
            {"errors": error.messages},
            400,
        )

    except ValueError as error:
        db.session.rollback()

        return make_response(
            {"error": str(error)},
            400,
        )


@app.route(
    "/workouts/<int:workout_id>",
    methods=["DELETE"],
)
def delete_workout(workout_id):
    workout = db.session.get(
        Workout,
        workout_id,
    )

    if workout is None:
        return make_response(
            {"error": "Workout not found"},
            404,
        )

    db.session.delete(workout)
    db.session.commit()

    return make_response(
        {"message": "Workout deleted successfully"},
        200,
    )


# -------------------------
# Exercise endpoints
# -------------------------


@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.order_by(
        Exercise.id
    ).all()

    return make_response(
        exercises_schema.dump(exercises),
        200,
    )


@app.route(
    "/exercises/<int:exercise_id>",
    methods=["GET"],
)
def get_exercise(exercise_id):
    exercise = db.session.get(
        Exercise,
        exercise_id,
    )

    if exercise is None:
        return make_response(
            {"error": "Exercise not found"},
            404,
        )

    return make_response(
        exercise_schema.dump(exercise),
        200,
    )


@app.route("/exercises", methods=["POST"])
def create_exercise():
    try:
        data = exercise_schema.load(
            request.get_json() or {}
        )

        exercise = Exercise(**data)

        db.session.add(exercise)
        db.session.commit()

        return make_response(
            exercise_schema.dump(exercise),
            201,
        )

    except ValidationError as error:
        return make_response(
            {"errors": error.messages},
            400,
        )

    except ValueError as error:
        db.session.rollback()

        return make_response(
            {"error": str(error)},
            400,
        )

    except IntegrityError:
        db.session.rollback()

        return make_response(
            {
                "error":
                "An exercise with that name already exists."
            },
            400,
        )


@app.route(
    "/exercises/<int:exercise_id>",
    methods=["DELETE"],
)
def delete_exercise(exercise_id):
    exercise = db.session.get(
        Exercise,
        exercise_id,
    )

    if exercise is None:
        return make_response(
            {"error": "Exercise not found"},
            404,
        )

    db.session.delete(exercise)
    db.session.commit()

    return make_response(
        {"message": "Exercise deleted successfully"},
        200,
    )


# -------------------------
# WorkoutExercise endpoint
# -------------------------


@app.route(
    "/workouts/<int:workout_id>"
    "/exercises/<int:exercise_id>"
    "/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(
    workout_id,
    exercise_id,
):
    workout = db.session.get(
        Workout,
        workout_id,
    )

    if workout is None:
        return make_response(
            {"error": "Workout not found"},
            404,
        )

    exercise = db.session.get(
        Exercise,
        exercise_id,
    )

    if exercise is None:
        return make_response(
            {"error": "Exercise not found"},
            404,
        )

    existing = WorkoutExercise.query.filter_by(
        workout_id=workout_id,
        exercise_id=exercise_id,
    ).first()

    if existing is not None:
        return make_response(
            {
                "error":
                "Exercise is already part of this workout."
            },
            400,
        )

    try:
        data = workout_exercise_schema.load(
            request.get_json() or {}
        )

        workout_exercise = WorkoutExercise(
            workout=workout,
            exercise=exercise,
            **data,
        )

        db.session.add(workout_exercise)
        db.session.commit()

        return make_response(
            workout_exercise_schema.dump(
                workout_exercise
            ),
            201,
        )

    except ValidationError as error:
        return make_response(
            {"errors": error.messages},
            400,
        )

    except ValueError as error:
        db.session.rollback()

        return make_response(
            {"error": str(error)},
            400,
        )

    except IntegrityError:
        db.session.rollback()

        return make_response(
            {
                "error":
                "Unable to add exercise to workout."
            },
            400,
        )


if __name__ == "__main__":
    app.run(
        port=5555,
        debug=True,
    )