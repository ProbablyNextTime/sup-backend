from jetkit.api.auth import blp, use_core_auth_api, use_sign_up_api  # noqa: F401
from supbackend.model.user import User
from .schema import UserSchema

use_core_auth_api(auth_model=User, user_schema=UserSchema)
use_sign_up_api(
    auth_model=User, allowed_domains="*", allowed_emails="*",
)
