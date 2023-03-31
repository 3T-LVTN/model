
from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette_context.middleware import ContextMiddleware
from app.common.context import Context

reusable_oauth2 = HTTPBearer(
    scheme_name='Authorization'
)


class CustomContextMiddleware(ContextMiddleware):
    async def set_context(self, request: Request) -> dict:

        # currently no authorization requirement
        # scheme, token = get_authorization_scheme_param(request.headers.get('Authorization'))

        # if scheme.lower() != "bearer":
        #     return dict()

        return {
            "ctx": Context(
                method=request.method
            )
        }
