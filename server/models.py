from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy


metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    workouts = association_proxy(
        "workout_exercises",
        "workout",
        creator=lambda workout: WorkoutExercise(workout=workout),
    )

    __table_args__ = (
        db.CheckConstraint(
            "length(trim(name)) > 0",
            name="exercise_name_not_blank",
        ),
    )

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name is required.")

        return value.strip()

    def __repr__(self):
        return (
            f"<Exercise {self.id}: "
            f"{self.name}, category={self.category}>"
        )


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    exercises = association_proxy(
        "workout_exercises",
        "exercise",
        creator=lambda exercise: WorkoutExercise(exercise=exercise),
    )

    __table_args__ = (
        db.CheckConstraint(
            "duration_minutes > 0",
            name="workout_duration_positive",
        ),
    )

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        if value is None or value <= 0:
            raise ValueError(
                "Workout duration must be greater than zero."
            )

        return value

    def __repr__(self):
        return (
            f"<Workout {self.id}: "
            f"{self.date}, {self.duration_minutes} minutes>"
        )


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)

    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id"),
        nullable=False,
    )

    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id"),
        nullable=False,
    )

    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship(
        "Workout",
        back_populates="workout_exercises",
    )

    exercise = db.relationship(
        "Exercise",
        back_populates="workout_exercises",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "workout_id",
            "exercise_id",
            name="uq_workout_exercise_pair",
        ),
        db.CheckConstraint(
            "reps IS NULL OR reps > 0",
            name="reps_positive",
        ),
        db.CheckConstraint(
            "sets IS NULL OR sets > 0",
            name="sets_positive",
        ),
        db.CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="duration_seconds_positive",
        ),
    )

    @validates("reps", "sets", "duration_seconds")
    def validate_positive_values(self, key, value):
        if value is not None and value <= 0:
            raise ValueError(
                f"{key} must be greater than zero when provided."
            )

        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise {self.id}: "
            f"workout={self.workout_id}, "
            f"exercise={self.exercise_id}>"
        )