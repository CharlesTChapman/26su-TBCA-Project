from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error


university_explorer_routes = Blueprint("university_explorer", __name__)


# ---- Helper functions -------------------------------------------------------
def _next_id(cursor, table):
    """Compute the next integer id for a table."""
    cursor.execute(f"SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM {table}")
    return cursor.fetchone()["next_id"]


# ---- Universities -----------------------------------------------------------
@university_explorer_routes.route("/universities", methods=["GET"])
def get_universities():
    """Get every university."""
    current_app.logger.info("GET /universities")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute("SELECT id, name, location FROM university")
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /universities failed: {e}")
        return error_response("Could not retrieve universities")


@university_explorer_routes.route("/universities/<int:university_id>", methods=["GET"])
def get_university(university_id):
    """Get the specifics of one university."""
    current_app.logger.info(f"GET /universities/{university_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, location FROM university WHERE id = %s",
            (university_id,),
        )
        university = cursor.fetchone()
        if university is None:
            return error_response("University not found", 404)
        return jsonify(university), 200
    except Error as e:
        current_app.logger.error(f"GET /universities/{university_id} failed: {e}")
        return error_response("Could not retrieve university")


# ---- Students ---------------------------------------------------------------
@university_explorer_routes.route("/students", methods=["GET"])
def get_students():
    """Get all students."""
    current_app.logger.info("GET /students")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute("SELECT id, first_name, last_name, email, address, major FROM student")
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /students failed: {e}")
        return error_response("Could not retrieve students")


@university_explorer_routes.route("/students", methods=["POST"])
def create_student():
    """Create a new student account."""
    current_app.logger.info("POST /students")
    data = request.get_json(silent=True) or {}
    if not data.get("first_name") or not data.get("last_name") or not data.get("email"):
        return error_response("'first_name', 'last_name' and 'email' are required", 400)
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        student_id = data.get("id") or _next_id(cursor, "student")
        cursor.execute(
            """INSERT INTO student (id, first_name, last_name, email, address, major)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (student_id, data["first_name"], data["last_name"], data["email"],
             data.get("address"), data.get("major")), # type: ignore
        )
        db.commit()
        return jsonify({"id": student_id, "message": "Student created"}), 201
    except Error as e:
        current_app.logger.error(f"POST /students failed: {e}")
        return error_response("Could not create student", 400)


@university_explorer_routes.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    """Get a specific student's account."""
    current_app.logger.info(f"GET /students/{student_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            "SELECT id, first_name, last_name, email, address, major FROM student WHERE id = %s",
            (student_id,),
        )
        student = cursor.fetchone()
        if student is None:
            return error_response("Student not found", 404)
        return jsonify(student), 200
    except Error as e:
        current_app.logger.error(f"GET /students/{student_id} failed: {e}")
        return error_response("Could not retrieve student")


@university_explorer_routes.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    """Update a specific student's account."""
    current_app.logger.info(f"PUT /students/{student_id}")
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE student
                  SET first_name = COALESCE(%s, first_name),
                      last_name  = COALESCE(%s, last_name),
                      email      = COALESCE(%s, email),
                      address    = COALESCE(%s, address),
                      major      = COALESCE(%s, major)
                WHERE id = %s""",
            (data.get("first_name"), data.get("last_name"), data.get("email"),
             data.get("address"), data.get("major"), student_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Student not found", 404)
        return jsonify({"message": "Student updated"}), 200
    except Error as e:
        current_app.logger.error(f"PUT /students/{student_id} failed: {e}")
        return error_response("Could not update student", 400)


@university_explorer_routes.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    """Delete a specific student's account."""
    current_app.logger.info(f"DELETE /students/{student_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM student WHERE id = %s", (student_id,))
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Student not found", 404)
        return jsonify({"message": "Student deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DELETE /students/{student_id} failed: {e}")
        return error_response("Could not delete student", 400)


# ---- Favorites --------------------------------------------------------------
@university_explorer_routes.route("/favorites/<int:student_id>", methods=["GET"])
def get_favorites(student_id):
    """Get all universities that a specific student has favorited."""
    current_app.logger.info(f"GET /favorites/{student_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT u.id, u.name, u.location, f.created_at
                 FROM favorites f
                 JOIN university u ON u.id = f.university_id
                WHERE f.student_id = %s""",
            (student_id,),
        )
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /favorites/{student_id} failed: {e}")
        return error_response("Could not retrieve favorites")


@university_explorer_routes.route(
    "/favorites/<int:student_id>/<int:university_id>", methods=["GET"])
def get_favorite(student_id, university_id):
    """Check whether a specific university is favorited.
    Returns 'True' if favorited and 'False' if not favorited"""
    current_app.logger.info(f"GET /favorites/{student_id}/{university_id}")
    try:
        cursor = get_db().cursor()
        cursor.execute(
            """SELECT 1
                 FROM favorites
                WHERE student_id = %s AND university_id = %s""",
            (student_id, university_id),
        )
        favorited = cursor.fetchone() is not None
        return jsonify({"favorited": favorited}), 200
    except Error as e:
        current_app.logger.error(f"GET favorite failed: {e}")
        return error_response("Could not retrieve favorite")


@university_explorer_routes.route(
    "/favorites/<int:student_id>/<int:university_id>", methods=["POST"])
def toggle_favorite(student_id, university_id):
    """Toggle a favorite for a student
    If the favorited row exists in the table it deletes it.
    If the favorited row does not exist in the table it creates it.
    """
    current_app.logger.info(f"POST /favorites/{student_id}/{university_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        # First queries for the favorite to see whether it already exists
        cursor.execute(
            """SELECT 1
                 FROM favorites
                WHERE student_id = %s AND university_id = %s""",
            (student_id, university_id),
        )
        exists = cursor.fetchone() is not None

        if exists:
            # If the row exists, remove it
            cursor.execute(
                """DELETE FROM favorites
                    WHERE student_id = %s AND university_id = %s""",
                (student_id, university_id),
            )
            db.commit()
            return jsonify({"favorited": False}), 200

        # If the row doesn't exist, add it
        cursor.execute(
            "INSERT INTO favorites (student_id, university_id) VALUES (%s, %s)",
            (student_id, university_id),
        )
        db.commit()
        return jsonify({"favorited": True}), 200
    except Error as e:
        current_app.logger.error(f"POST favorite toggle failed: {e}")
        return error_response("Could not toggle favorite", 400)


# ---- Pros / Cons ------------------------------------------------------------
@university_explorer_routes.route(
    "/pros_cons/<int:student_id>/<int:university_id>", methods=["GET"])
def get_pros_cons(student_id, university_id):
    """Get student's pros/cons for a university."""
    current_app.logger.info(f"GET /pros_cons/{student_id}/{university_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT student_id, university_id, pros, cons, created_at, updated_at
                 FROM pros_cons
                WHERE student_id = %s AND university_id = %s""",
            (student_id, university_id),
        )
        record = cursor.fetchone()
        if record is None:
            return error_response("Pros/cons list not found", 404)
        return jsonify(record), 200
    except Error as e:
        current_app.logger.error(f"GET pros_cons failed: {e}")
        return error_response("Could not retrieve pros/cons")


@university_explorer_routes.route(
    "/pros_cons/<int:student_id>/<int:university_id>", methods=["POST"])
def create_pros_cons(student_id, university_id):
    """Create student's pros/cons list for a university."""
    current_app.logger.info(f"POST /pros_cons/{student_id}/{university_id}")
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO pros_cons (student_id, university_id, pros, cons)
               VALUES (%s, %s, %s, %s)""",
            (student_id, university_id, data.get("pros"), data.get("cons")),
        )
        db.commit()
        return jsonify({"message": "Pros/cons list created"}), 201
    except Error as e:
        current_app.logger.error(f"POST pros_cons failed: {e}")
        return error_response("Could not create pros/cons", 400)


@university_explorer_routes.route(
    "/pros_cons/<int:student_id>/<int:university_id>", methods=["PUT"])
def update_pros_cons(student_id, university_id):
    """Update student's pros/cons list for a university."""
    current_app.logger.info(f"PUT /pros_cons/{student_id}/{university_id}")
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE pros_cons
                  SET pros       = COALESCE(%s, pros),
                      cons       = COALESCE(%s, cons),
                      updated_at = CURRENT_TIMESTAMP
                WHERE student_id = %s AND university_id = %s""",
            (data.get("pros"), data.get("cons"), student_id, university_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Pros/cons list not found", 404)
        return jsonify({"message": "Pros/cons list updated"}), 200
    except Error as e:
        current_app.logger.error(f"PUT pros_cons failed: {e}")
        return error_response("Could not update pros/cons", 400)


@university_explorer_routes.route(
    "/pros_cons/<int:student_id>/<int:university_id>", methods=["DELETE"])
def delete_pros_cons(student_id, university_id):
    """Delete student's pros/cons list for a university."""
    current_app.logger.info(f"DELETE /pros_cons/{student_id}/{university_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """DELETE FROM pros_cons
                WHERE student_id = %s AND university_id = %s""",
            (student_id, university_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Pros/cons list not found", 404)
        return jsonify({"message": "Pros/cons list deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DELETE pros_cons failed: {e}")
        return error_response("Could not delete pros/cons", 400)

#Survery From
@university_explorer_routes.route("/survey_form/<int:student_id>", methods=["GET"])
def get_survey_form(student_id):
    """Get a student's survery responses"""
    current_app.logger.info(f"GET /survey_form/{student_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            "SELECT student_id, student_budget, student_degree_level, student_size, created_at, updated_at FROM survey_form WHERE student_id = %s",
            (student_id,),
        )
        record = cursor.fetchone()
        if record is None:
            return error_response("Survey not found", 404)
        return jsonify(record), 200
    except Error as e:
        current_app.logger.error(f"GET /survey_form/{student_id} failed: {e}")
        return error_response("Could not retrieve survey form")
    
@university_explorer_routes.route("/survey_form/<int:student_id>", methods=["POST"])
def create_survey_form(student_id):
    """Create a student's survey and mark as completed"""
    current_app.logger.info(f"POST /survey_form/{student_id}")
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO survey_form (student_id, student_budget, student_degree_level, student_size)
               VALUES (%s, %s, %s, %s)""",
            (student_id, data.get("student_budget"), data.get("student_degree_level"), data.get("student_size")),
        )
        db.commit()
        return jsonify({"message": "Survey form created"}), 201
    except Error as e:
        current_app.logger.error(f"POST /survey_form/{student_id} failed: {e}")
        return error_response("Could not create survey form", 400)
    
@university_explorer_routes.route("/survey_form/<int:student_id>", methods=["PUT"])
def update_survey_form(student_id):
    """Update a student's survey responses."""
    current_app.logger.info(f"PUT /survey_form/{student_id}")
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE survey_form
                  SET student_budget       = COALESCE(%s, student_budget),
                      student_degree_level = COALESCE(%s, student_degree_level),
                      student_size         = COALESCE(%s, student_size),
                      updated_at           = CURRENT_TIMESTAMP
                WHERE student_id = %s""",
            (data.get("student_budget"), data.get("student_degree_level"), data.get("student_size"), student_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Survey form not found", 404)
        return jsonify({"message": "Survey form updated"}), 200
    except Error as e:
        current_app.logger.error(f"PUT /survey_form/{student_id} failed: {e}")
        return error_response("Could not update survey form", 400)