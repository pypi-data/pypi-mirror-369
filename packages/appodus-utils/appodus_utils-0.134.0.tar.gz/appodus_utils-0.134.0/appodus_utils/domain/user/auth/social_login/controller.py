from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from kink import di
from starlette import status
from starlette.responses import Response, RedirectResponse

from appodus_utils import Utils
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.domain.user.auth.models import SocialAuthOperationType, OAuthCallbackRequest, SocialLoginUserInfo
from appodus_utils.domain.user.auth.service import AuthService
from appodus_utils.domain.user.auth.social_login.factory import SocialAuthProviderFactory
from appodus_utils.domain.user.auth.social_login.interface import ISocialAuthProvider
from appodus_utils.domain.user.auth.social_login.models import SocialAuthPlatform, OAuthRequestStoredState

SOCIAL_LOGIN_CALLBACK_PATH = Utils.get_from_env_fail_if_not_exists("SOCIAL_LOGIN_CALLBACK_PATH")

social_auth_router = APIRouter(prefix=SOCIAL_LOGIN_CALLBACK_PATH, tags=["Social Auth"])
social_auth_service_factory: SocialAuthProviderFactory = di[SocialAuthProviderFactory]
auth_service: AuthService = di[AuthService]


@social_auth_router.get("/{provider}")
async def auth_callback(provider: SocialAuthPlatform, request: Request, response: Response, code: str = None, state: str = None):
    # Verify state
    stored_state: OAuthRequestStoredState = await RedisUtils.get_redis(state)
    if not stored_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Get stored code_verifier
    if not stored_state.code_verifier:
        raise HTTPException(status_code=400, detail="Missing code_verifier")

    auth_provider = social_auth_service_factory.get_auth_provider(provider)

    payload = OAuthCallbackRequest(
        code=code,
        code_verifier=stored_state.code_verifier,
        operation_type=stored_state.operation_type,
        redirect_uri=stored_state.redirect_uri,
        frontend_origin=stored_state.frontend_origin
    )
    user_info = await auth_provider.verify(payload, request)

    user_info = await auth_service.social_login_signup(user_info)

    return build_redirect_response(response=response, user_info=user_info)


@social_auth_router.get("/{provider}/init")
async def init_social_auth(provider: SocialAuthPlatform, operation_type: SocialAuthOperationType, request: Request):
    auth_provider: ISocialAuthProvider = social_auth_service_factory.get_auth_provider(provider)

    response = await auth_provider.initialize(operation_type, request)
    return {"redirectUrl": response["url"]}

def build_redirect_response(response: Response, user_info: SocialLoginUserInfo):
    redirect = RedirectResponse(url=f"{user_info.frontend_origin}?"
                                    f"code={user_info.response_code}&"
                                    f"message={user_info.response_message}&"
                                    f"firstname={user_info.firstname}&"
                                    f"lastname={user_info.lastname}",
                                status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    for header, value in response.raw_headers:
        if header.lower() == b"set-cookie":
            redirect.headers.append(header.decode(), value.decode())

    return redirect
