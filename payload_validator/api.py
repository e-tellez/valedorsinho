import logging

from flask import Blueprint, Response, request, jsonify

from payload_validator.validator import validate_payments_payload

logger = logging.getLogger(__name__)

bp = Blueprint("payload_validator_api", __name__)


@bp.route("/api/validate-payload", methods=["POST"])
def validate_payload() -> tuple[Response, int]:
    """Validate a /payments JSON payload against the OpenAPI spec.

    Expects a JSON body with a ``payload`` key containing the raw
    /payments request object.  Returns validation errors (if any).
    """
    body = request.get_json(silent=True)
    if not body or "payload" not in body:
        return jsonify({"error": "Request must include a 'payload' key."}), 400

    payload = body["payload"]
    if not isinstance(payload, dict):
        return jsonify({"error": "'payload' must be a JSON object."}), 400

    try:
        errors = validate_payments_payload(payload)
    except Exception as exception:
        logger.exception("Validation failed")
        return jsonify({"error": f"Validation error: {exception}"}), 500

    return jsonify({"valid": len(errors) == 0, "errors": errors}), 200
