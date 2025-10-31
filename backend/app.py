"""Flask backend that serves scenic spot data to the frontend."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, Dict, Iterable

from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from storage import (
    StorageError,
    append_detail_section,
    delete_spot,
    get_spot,
    list_spots,
    upsert_spot,
)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.after_request
    def add_cors_headers(response):
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type")
        response.headers.setdefault(
            "Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS"
        )
        return response

    @app.route("/api/health", methods=["GET"])
    def healthcheck():
        return jsonify(status="ok"), HTTPStatus.OK

    @app.route("/api/spots", methods=["GET", "OPTIONS"])
    def spots_collection():
        if request.method == "OPTIONS":
            return "", HTTPStatus.NO_CONTENT

        spots = list_spots()
        return jsonify(spots=spots, count=len(spots)), HTTPStatus.OK

    @app.route("/api/spots/<spot_id>", methods=["GET", "OPTIONS"])
    def spot_detail(spot_id: str):
        if request.method == "OPTIONS":
            return "", HTTPStatus.NO_CONTENT

        record = get_spot(spot_id)
        if not record:
            return (
                jsonify(error="Spot not found", spot_id=spot_id),
                HTTPStatus.NOT_FOUND,
            )
        return jsonify(record), HTTPStatus.OK

    @app.route("/api/spots", methods=["POST"])
    def create_spot():
        payload = _require_json_body(required_fields=("id", "name"))
        try:
            record = upsert_spot(payload)
        except StorageError as exc:
            return jsonify(error=str(exc)), HTTPStatus.BAD_REQUEST
        return jsonify(record), HTTPStatus.CREATED

    @app.route("/api/spots/<spot_id>", methods=["PUT", "PATCH"])
    def update_spot(spot_id: str):
        payload = _require_json_body()
        payload.setdefault("id", spot_id)
        try:
            record = upsert_spot(payload)
        except StorageError as exc:
            return jsonify(error=str(exc)), HTTPStatus.BAD_REQUEST
        return jsonify(record), HTTPStatus.OK

    @app.route("/api/spots/<spot_id>", methods=["DELETE"])
    def remove_spot(spot_id: str):
        deleted = delete_spot(spot_id)
        status = HTTPStatus.NO_CONTENT if deleted else HTTPStatus.NOT_FOUND
        if deleted:
            return "", status
        return jsonify(error="Spot not found", spot_id=spot_id), status

    @app.route("/admin/spots/new", methods=["GET", "POST"])
    def admin_create_spot():
        context: Dict[str, Any] = {
            "errors": [],
            "submitted": False,
            "prefill": {},
        }

        if request.method == "POST":
            form = request.form
            record = {
                "id": form.get("id", "").strip(),
                "name": form.get("name", "").strip(),
                "location": form.get("location", "").strip(),
                "summary": form.get("summary", "").strip(),
                "heroImage": form.get("heroImage", "").strip(),
                "thumbnail": form.get("thumbnail", "").strip(),
                "tags": [
                    tag.strip()
                    for tag in form.get("tags", "").split(",")
                    if tag.strip()
                ],
                "detailSections": [],
            }

            missing = [key for key in ("id", "name") if not record[key]]
            if missing:
                context["errors"].append(
                    f"以下字段为必填: {', '.join(missing)}"
                )
                context["prefill"] = record
            else:
                try:
                    upsert_spot(record)
                except StorageError as exc:
                    context["errors"].append(str(exc))
                    context["prefill"] = record
                else:
                    return redirect(
                        url_for(
                            "admin_create_detail",
                            spot_id=record["id"],
                            created="1",
                        )
                    )

        return render_template(
            "admin/create_spot.html",
            context=context,
            spots=list_spots(),
        )

    @app.route("/admin/spots/<spot_id>/details/new", methods=["GET", "POST"])
    def admin_create_detail(spot_id: str):
        spot = get_spot(spot_id)
        if not spot:
            abort(HTTPStatus.NOT_FOUND)

        context: Dict[str, Any] = {
            "errors": [],
            "submitted": False,
            "prefill": {},
            "spot": spot,
        }

        if request.method == "POST":
            form = request.form
            raw_paragraphs = form.get("paragraphs", "")
            paragraphs = [
                block.strip()
                for block in raw_paragraphs.splitlines()
                if block.strip()
            ]

            section = {
                "title": form.get("title", "").strip(),
                "emphasis": form.get("emphasis", "").strip(),
                "paragraphs": paragraphs,
                "image": form.get("image", "").strip(),
                "imageAlt": form.get("imageAlt", "").strip(),
            }

            required = [key for key in ("title", "image") if not section[key]]
            if required:
                context["errors"].append(
                    f"以下字段为必填: {', '.join(required)}"
                )
                context["prefill"] = {**section, "paragraphs": raw_paragraphs}
            else:
                try:
                    append_detail_section(spot_id, section)
                except StorageError as exc:
                    context["errors"].append(str(exc))
                    context["prefill"] = {**section, "paragraphs": raw_paragraphs}
                else:
                    context["submitted"] = True
                    context["prefill"] = {}
                    spot = get_spot(spot_id)
                    context["spot"] = spot

        return render_template(
            "admin/create_detail.html",
            context=context,
            spot=spot,
        )

    return app


def _require_json_body(required_fields: Iterable[str] | None = None) -> Dict[str, Any]:
    if not request.is_json:
        _abort_with_json(
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            "Expected 'application/json' request body",
        )

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        _abort_with_json(HTTPStatus.BAD_REQUEST, "Malformed JSON body")

    if required_fields:
        missing = [field for field in required_fields if field not in payload]
        if missing:
            _abort_with_json(
                HTTPStatus.BAD_REQUEST,
                "Missing required fields",
                fields=missing,
            )

    return payload


def _abort_with_json(status: HTTPStatus, message: str, **details: Any) -> None:
    response = jsonify({"error": message, **details})
    abort(make_response(response, status))


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
