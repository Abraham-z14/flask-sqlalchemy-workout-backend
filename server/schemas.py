from marshmallow import (
    Schema,
    fields,
    validate,
)


class ExerciseSummarySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    category = fields.String()
    equipment_needed = fields.Boolean()


class WorkoutSummarySchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date()
    duration_minutes = fields.Integer()
    notes = fields.String(allow_none=True)


class WorkoutExerciseForWorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    reps = fields.Integer(allow_none=True)
    sets = fields.Integer(allow_none=True)
    duration_seconds = fields.Integer(allow_none=True)

    exercise = fields.Nested(
        ExerciseSummarySchema,
        dump_only=True,
    )


class WorkoutExerciseForExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    reps = fields.Integer(allow_none=True)
    sets = fields.Integer(allow_none=True)
    duration_seconds = fields.Integer(allow_none=True)

    workout = fields.Nested(
        WorkoutSummarySchema,
        dump_only=True,
    )


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)

    name = fields.String(
        required=True,
        validate=validate.Length(
            min=1,
            error="Exercise name cannot be blank.",
        ),
    )

    category = fields.String(
        required=True,
        validate=validate.Length(
            min=1,
            error="Exercise category cannot be blank.",
        ),
    )

    equipment_needed = fields.Boolean(
        required=True,
    )

    workouts = fields.Nested(
        WorkoutSummarySchema,
        many=True,
        dump_only=True,
    )

    workout_exercises = fields.Nested(
        WorkoutExerciseForExerciseSchema,
        many=True,
        dump_only=True,
    )


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)

    date = fields.Date(
        required=True,
    )

    duration_minutes = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1,
            error="Workout duration must be greater than zero.",
        ),
    )

    notes = fields.String(
        allow_none=True,
        load_default=None,
    )

    exercises = fields.Nested(
        ExerciseSummarySchema,
        many=True,
        dump_only=True,
    )

    workout_exercises = fields.Nested(
        WorkoutExerciseForWorkoutSchema,
        many=True,
        dump_only=True,
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)

    workout_id = fields.Integer(
        dump_only=True,
    )

    exercise_id = fields.Integer(
        dump_only=True,
    )

    reps = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(
            min=1,
            error="Reps must be greater than zero.",
        ),
    )

    sets = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(
            min=1,
            error="Sets must be greater than zero.",
        ),
    )

    duration_seconds = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(
            min=1,
            error="Duration must be greater than zero.",
        ),
    )

    workout = fields.Nested(
        WorkoutSummarySchema,
        dump_only=True,
    )

    exercise = fields.Nested(
        ExerciseSummarySchema,
        dump_only=True,
    )