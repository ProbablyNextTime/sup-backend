from flask_jwt_extended import current_user, jwt_required
from flask_smorest import Blueprint, abort

from supbackend.api.auth.schema import MeSchema

blp = Blueprint("Me", __name__, url_prefix="/api/me")


@blp.route("", methods=["GET"])
@blp.response(MeSchema)
@jwt_required
def me():
    if current_user:
        return current_user
    else:
        abort(401)
