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
        cursor.execute(
            "SELECT id, name, location, student_fees, per_student_fees, highest_degree, staff_fte, web_pages "
            "FROM university"
        )
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
            "SELECT id, name, location, student_fees, per_student_fees, highest_degree, staff_fte, web_pages "
            "FROM university WHERE id = %s",
            (university_id,),
        )
        university = cursor.fetchone()
        if university is None:
            return error_response("University not found", 404)
        return jsonify(university), 200
    except Error as e:
        current_app.logger.error(f"GET /universities/{university_id} failed: {e}")
        return error_response("Could not retrieve university")


# ---- Labor statisticians ----------------------------------------------------
@university_explorer_routes.route("/labor_statisticians", methods=["GET"])
def get_labor_statisticians():
    """Get all labor statisticians."""
    current_app.logger.info("GET /labor_statisticians")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute("SELECT id, first_name, last_name, email FROM labor_statistician")
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /labor_statisticians failed: {e}")
        return error_response("Could not retrieve labor statisticians")


# ---- Budget managers --------------------------------------------------------
@university_explorer_routes.route("/budget_managers", methods=["GET"])
def get_budget_managers():
    """Get all budget managers."""
    current_app.logger.info("GET /budget_managers")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute("SELECT id, first_name, last_name, email FROM budget_manager")
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /budget_managers failed: {e}")
        return error_response("Could not retrieve budget managers")


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
            """SELECT u.id, u.name, u.location, u.student_fees, u.per_student_fees, u.highest_degree,
                      u.staff_fte, f.created_at
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

# ---- Survey Form ------------------------------------------------------------
@university_explorer_routes.route("/survey_form/<int:student_id>", methods=["GET"])
def get_survey_form(student_id):
    """Get a student's survery responses"""
    current_app.logger.info(f"GET /survey_form/{student_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT student_id, student_budget, student_degree_level, student_size,
                      student_major, student_country, student_proximity_min,
                      student_proximity_max, student_campus_type, student_financial_aid,
                      created_at, updated_at
                 FROM survey_form WHERE student_id = %s""",
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
            """INSERT INTO survey_form
                   (student_id, student_budget, student_degree_level, student_size,
                    student_major, student_country, student_proximity_min,
                    student_proximity_max, student_campus_type, student_financial_aid)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (student_id, data.get("student_budget"), data.get("student_degree_level"),
             data.get("student_size"), data.get("student_major"), data.get("student_country"),
             data.get("student_proximity_min"), data.get("student_proximity_max"),
             data.get("student_campus_type"), data.get("student_financial_aid")),
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
                  SET student_budget        = COALESCE(%s, student_budget),
                      student_degree_level  = COALESCE(%s, student_degree_level),
                      student_size          = COALESCE(%s, student_size),
                      student_major         = COALESCE(%s, student_major),
                      student_country       = COALESCE(%s, student_country),
                      student_proximity_min = COALESCE(%s, student_proximity_min),
                      student_proximity_max = COALESCE(%s, student_proximity_max),
                      student_campus_type   = COALESCE(%s, student_campus_type),
                      student_financial_aid = COALESCE(%s, student_financial_aid),
                      updated_at            = CURRENT_TIMESTAMP
                WHERE student_id = %s""",
            (data.get("student_budget"), data.get("student_degree_level"), data.get("student_size"),
             data.get("student_major"), data.get("student_country"), data.get("student_proximity_min"),
             data.get("student_proximity_max"), data.get("student_campus_type"),
             data.get("student_financial_aid"), student_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Survey form not found", 404)
        return jsonify({"message": "Survey form updated"}), 200
    except Error as e:
        current_app.logger.error(f"PUT /survey_form/{student_id} failed: {e}")
        return error_response("Could not update survey form", 400)
    
@university_explorer_routes.route("/survey_form/<int:student_id>", methods=["DELETE"])
def delete_survey_form(student_id):
    """Delete a student's survey responses."""
    current_app.logger.info(f"DELETE /survey_form/{student_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM survey_form WHERE student_id = %s", (student_id,))
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Survey form not found", 404)
        return jsonify({"message": "Survey form deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DELETE /survey_form/{student_id} failed: {e}")
        return error_response("Could not delete survey form", 400)


# ---- Recommended Universities -----------------------------------------------
@university_explorer_routes.route(
    "/students/<int:student_id>/recommended_universities", methods=["GET"])
def get_recommendations(student_id):
    """Get the universities recommended to a student."""
    current_app.logger.info(
        f"GET /students/{student_id}/recommended_universities")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT u.id, u.name, u.location, r.created_at
                 FROM recommendations r
                 JOIN university u ON u.id = r.university_id
                WHERE r.student_id = %s""",
            (student_id,),
        )
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(
            f"GET /students/{student_id}/recommended_universities failed: {e}")
        return error_response("Could not retrieve recommendations")


@university_explorer_routes.route(
    "/students/<int:student_id>/recommended_universities/<int:university_id>",
    methods=["POST"])
def add_recommendation(student_id, university_id):
    """Recommend a university to a student."""
    current_app.logger.info(
        f"POST /students/{student_id}/recommended_universities/{university_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO recommendations (student_id, university_id)
               VALUES (%s, %s)""",
            (student_id, university_id),
        )
        db.commit()
        return jsonify({"message": "Recommendation added"}), 201
    except Error as e:
        current_app.logger.error(f"POST recommendations failed: {e}")
        return error_response("Could not add recommendation", 400)


@university_explorer_routes.route(
    "/students/<int:student_id>/recommended_universities/<int:university_id>",
    methods=["DELETE"])
def delete_recommendation(student_id, university_id):
    """Delete a student's recommendation."""
    current_app.logger.info(
        f"DELETE /students/{student_id}/recommended_universities/{university_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """DELETE FROM recommendations
                WHERE student_id = %s AND university_id = %s""",
            (student_id, university_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Recommendation not found", 404)
        return jsonify({"message": "Recommendation deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DELETE recommendations failed: {e}")
        return error_response("Could not delete recommendation", 400)


# ---- Labor statistician account management ----------------------------------
@university_explorer_routes.route("/labor_statisticians", methods=["POST"])
def create_labor_statistician():
    """Create a new labor statistician account."""
    current_app.logger.info("POST /labor_statisticians")
    data = request.get_json(silent=True) or {}
    if not data.get("first_name") or not data.get("last_name") or not data.get("email"):
        return error_response("'first_name', 'last_name' and 'email' are required", 400)
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        stat_id = data.get("id") or _next_id(cursor, "labor_statistician")
        cursor.execute(
            """INSERT INTO labor_statistician (id, first_name, last_name, email)
               VALUES (%s, %s, %s, %s)""",
            (stat_id, data["first_name"], data["last_name"], data["email"]),
        )
        db.commit()
        return jsonify({"id": stat_id, "message": "Labor statistician created"}), 201
    except Error as e:
        current_app.logger.error(f"POST /labor_statisticians failed: {e}")
        return error_response("Could not create labor statistician", 400)


@university_explorer_routes.route(
    "/labor_statisticians/<int:labor_statistician_id>", methods=["GET"])
def get_labor_statistician(labor_statistician_id):
    """Get a specific labor statistician's account."""
    current_app.logger.info(f"GET /labor_statisticians/{labor_statistician_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            "SELECT id, first_name, last_name, email FROM labor_statistician WHERE id = %s",
            (labor_statistician_id,),
        )
        stat = cursor.fetchone()
        if stat is None:
            return error_response("Labor statistician not found", 404)
        return jsonify(stat), 200
    except Error as e:
        current_app.logger.error(f"GET labor_statistician failed: {e}")
        return error_response("Could not retrieve labor statistician")


@university_explorer_routes.route(
    "/labor_statisticians/<int:labor_statistician_id>", methods=["PUT"])
def update_labor_statistician(labor_statistician_id):
    """Update a specific labor statistician's account."""
    current_app.logger.info(f"PUT /labor_statisticians/{labor_statistician_id}")
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE labor_statistician
                  SET first_name = COALESCE(%s, first_name),
                      last_name  = COALESCE(%s, last_name),
                      email      = COALESCE(%s, email)
                WHERE id = %s""",
            (data.get("first_name"), data.get("last_name"), data.get("email"),
             labor_statistician_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Labor statistician not found", 404)
        return jsonify({"message": "Labor statistician updated"}), 200
    except Error as e:
        current_app.logger.error(f"PUT labor_statistician failed: {e}")
        return error_response("Could not update labor statistician", 400)


@university_explorer_routes.route(
    "/labor_statisticians/<int:labor_statistician_id>", methods=["DELETE"])
def delete_labor_statistician(labor_statistician_id):
    """Delete a specific labor statistician's account."""
    current_app.logger.info(f"DELETE /labor_statisticians/{labor_statistician_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM labor_statistician WHERE id = %s", (labor_statistician_id,)
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Labor statistician not found", 404)
        return jsonify({"message": "Labor statistician deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DELETE labor_statistician failed: {e}")
        return error_response("Could not delete labor statistician", 400)


# ---- Budget manager account management --------------------------------------
@university_explorer_routes.route("/budget_managers", methods=["POST"])
def create_budget_manager():
    """Create a new budget manager account."""
    current_app.logger.info("POST /budget_managers")
    data = request.get_json(silent=True) or {}
    if not data.get("first_name") or not data.get("last_name") or not data.get("email"):
        return error_response("'first_name', 'last_name' and 'email' are required", 400)
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        manager_id = data.get("id") or _next_id(cursor, "budget_manager")
        cursor.execute(
            """INSERT INTO budget_manager (id, first_name, last_name, email)
               VALUES (%s, %s, %s, %s)""",
            (manager_id, data["first_name"], data["last_name"], data["email"]),
        )
        db.commit()
        return jsonify({"id": manager_id, "message": "Budget manager created"}), 201
    except Error as e:
        current_app.logger.error(f"POST /budget_managers failed: {e}")
        return error_response("Could not create budget manager", 400)


@university_explorer_routes.route(
    "/budget_managers/<int:budget_manager_id>", methods=["GET"])
def get_budget_manager(budget_manager_id):
    """Get a specific budget manager's account."""
    current_app.logger.info(f"GET /budget_managers/{budget_manager_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            "SELECT id, first_name, last_name, email FROM budget_manager WHERE id = %s",
            (budget_manager_id,),
        )
        manager = cursor.fetchone()
        if manager is None:
            return error_response("Budget manager not found", 404)
        return jsonify(manager), 200
    except Error as e:
        current_app.logger.error(f"GET budget_manager failed: {e}")
        return error_response("Could not retrieve budget manager")


@university_explorer_routes.route(
    "/budget_managers/<int:budget_manager_id>", methods=["PUT"])
def update_budget_manager(budget_manager_id):
    """Update a specific budget manager's account."""
    current_app.logger.info(f"PUT /budget_managers/{budget_manager_id}")
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE budget_manager
                  SET first_name = COALESCE(%s, first_name),
                      last_name  = COALESCE(%s, last_name),
                      email      = COALESCE(%s, email)
                WHERE id = %s""",
            (data.get("first_name"), data.get("last_name"), data.get("email"),
             budget_manager_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Budget manager not found", 404)
        return jsonify({"message": "Budget manager updated"}), 200
    except Error as e:
        current_app.logger.error(f"PUT budget_manager failed: {e}")
        return error_response("Could not update budget manager", 400)


@university_explorer_routes.route(
    "/budget_managers/<int:budget_manager_id>", methods=["DELETE"])
def delete_budget_manager(budget_manager_id):
    """Delete a specific budget manager's account."""
    current_app.logger.info(f"DELETE /budget_managers/{budget_manager_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM budget_manager WHERE id = %s", (budget_manager_id,)
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Budget manager not found", 404)
        return jsonify({"message": "Budget manager deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DELETE budget_manager failed: {e}")
        return error_response("Could not delete budget manager", 400)


# ---- Stats ------------------------------------------------------------------
@university_explorer_routes.route("/stats/total_students", methods=["GET"])
def stats_total_students():
    """Get the total number of students."""
    current_app.logger.info("GET /stats/total_students")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total_students FROM student")
        return jsonify(cursor.fetchone()), 200
    except Error as e:
        current_app.logger.error(f"GET /stats/total_students failed: {e}")
        return error_response("Could not retrieve student total")


@university_explorer_routes.route("/stats/universities", methods=["GET"])
def stats_universities():
    """Get academic stats across all universities."""
    current_app.logger.info("GET /stats/universities")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT u.id, u.name, u.location,
                      ar.year, ar.students, ar.graduation_rate, ar.avg_gpa
                 FROM university u
                 LEFT JOIN academic_reports ar ON ar.university_id = u.id"""
        )
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /stats/universities failed: {e}")
        return error_response("Could not retrieve university stats")


@university_explorer_routes.route(
    "/stats/universities/<int:university_id>", methods=["GET"])
def stats_university(university_id):
    """Get academic stats for a specific university."""
    current_app.logger.info(f"GET /stats/universities/{university_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT u.id, u.name, u.location,
                      ar.year, ar.students, ar.graduation_rate, ar.avg_gpa
                 FROM university u
                 LEFT JOIN academic_reports ar ON ar.university_id = u.id
                WHERE u.id = %s""",
            (university_id,),
        )
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /stats/universities/{university_id} failed: {e}")
        return error_response("Could not retrieve university stats")


@university_explorer_routes.route("/stats/majors", methods=["GET"])
def stats_majors():
    """Get the distribution of majors across students."""
    current_app.logger.info("GET /stats/majors")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT major, COUNT(*) AS student_count
                 FROM student
                GROUP BY major
                ORDER BY student_count DESC"""
        )
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /stats/majors failed: {e}")
        return error_response("Could not retrieve major distribution")


@university_explorer_routes.route("/stats/budget/<int:university_id>", methods=["GET"])
def stats_budget(university_id):
    """Get budget information for a specific university."""
    current_app.logger.info(f"GET /stats/budget/{university_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT id AS plan_id, budget_manager_id, total_amount,
                      created_at, updated_at
                 FROM budget_plan
                WHERE university_id = %s""",
            (university_id,),
        )
        plans = cursor.fetchall()
        total = sum(p["total_amount"] or 0 for p in plans)
        return jsonify({
            "university_id": university_id,
            "plans": plans,
            "total_budget": total,
        }), 200
    except Error as e:
        current_app.logger.error(f"GET /stats/budget/{university_id} failed: {e}")
        return error_response("Could not retrieve budget stats")


# ---- Budget Plans -----------------------------------------------------------
@university_explorer_routes.route("/budget_plans", methods=["GET"])
def get_budget_plans():
    """Get all budget plans, optionally filtered by manager."""
    budget_manager_id = request.args.get("budget_manager_id")
    current_app.logger.info(
        f"GET /budget_plans (budget_manager_id={budget_manager_id})")
    try:
        cursor = get_db().cursor(dictionary=True)
        sql = """SELECT id, university_id, budget_manager_id, total_amount,
                        created_at, updated_at
                   FROM budget_plan"""
        params = ()
        if budget_manager_id is not None:
            sql += " WHERE budget_manager_id = %s"
            params = (budget_manager_id,)
        cursor.execute(sql, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"GET /budget_plans failed: {e}")
        return error_response("Could not retrieve budget plans")


@university_explorer_routes.route("/budget_plans/<int:plan_id>", methods=["GET"])
def get_budget_plan(plan_id):
    """Get a specific budget plan."""
    current_app.logger.info(f"GET /budget_plans/{plan_id}")
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            """SELECT id, university_id, budget_manager_id, total_amount,
                      created_at, updated_at
                 FROM budget_plan WHERE id = %s""",
            (plan_id,),
        )
        plan = cursor.fetchone()
        if plan is None:
            return error_response("Budget plan not found", 404)
        return jsonify(plan), 200
    except Error as e:
        current_app.logger.error(f"GET /budget_plans/{plan_id} failed: {e}")
        return error_response("Could not retrieve budget plan")


@university_explorer_routes.route("/budget_plans", methods=["POST"])
def create_budget_plan():
    """Create a new budget plan."""
    current_app.logger.info("POST /budget_plans")
    data = request.get_json(silent=True) or {}
    if not data.get("university_id") or not data.get("budget_manager_id"):
        return error_response(
            "'university_id' and 'budget_manager_id' are required", 400)
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        plan_id = data.get("id") or _next_id(cursor, "budget_plan")
        cursor.execute(
            """INSERT INTO budget_plan
                   (id, university_id, budget_manager_id, total_amount)
               VALUES (%s, %s, %s, %s)""",
            (plan_id, data["university_id"], data["budget_manager_id"],
             data.get("total_amount")),
        )
        db.commit()
        return jsonify({"id": plan_id, "message": "Budget plan created"}), 201
    except Error as e:
        current_app.logger.error(f"POST /budget_plans failed: {e}")
        return error_response("Could not create budget plan", 400)


@university_explorer_routes.route("/budget_plans/<int:plan_id>", methods=["PUT"])
def update_budget_plan(plan_id):
    """Update an existing budget plan."""
    current_app.logger.info(f"PUT /budget_plans/{plan_id}")
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE budget_plan
                  SET university_id     = COALESCE(%s, university_id),
                      budget_manager_id = COALESCE(%s, budget_manager_id),
                      total_amount      = COALESCE(%s, total_amount),
                      updated_at        = CURRENT_TIMESTAMP
                WHERE id = %s""",
            (data.get("university_id"), data.get("budget_manager_id"),
             data.get("total_amount"), plan_id),
        )
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Budget plan not found", 404)
        return jsonify({"message": "Budget plan updated"}), 200
    except Error as e:
        current_app.logger.error(f"PUT /budget_plans/{plan_id} failed: {e}")
        return error_response("Could not update budget plan", 400)


@university_explorer_routes.route("/budget_plans/<int:plan_id>", methods=["DELETE"])
def delete_budget_plan(plan_id):
    """Delete an existing budget plan."""
    current_app.logger.info(f"DELETE /budget_plans/{plan_id}")
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM budget_plan WHERE id = %s", (plan_id,))
        db.commit()
        if cursor.rowcount == 0:
            return error_response("Budget plan not found", 404)
        return jsonify({"message": "Budget plan deleted"}), 200
    except Error as e:
        current_app.logger.error(f"DELETE /budget_plans/{plan_id} failed: {e}")
        return error_response("Could not delete budget plan", 400)
