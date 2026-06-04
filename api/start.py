import asyncio
from netschoolpy import NetSchool, exceptions
from filek import LOGIN, PASSWORD, SCHOOL

_ESIA_API_HEADERS = {
    "content-type": "application/json",
    "origin": "https://esia.gosuslugi.ru",
    "referer": "https://esia.gosuslugi.ru/login/",
}

_orig_handle_esia_mfa = NetSchool._handle_esia_mfa


async def _patched_handle_esia_mfa(self, esia_client, login_data, otp_callback=None):
    """Патч: принимает статус 202 от verify (оригинал принимает только 200/201)."""
    mfa_details = login_data.get("mfa_details", {})
    mfa_type = str(mfa_details.get("type", "")).upper()
    if mfa_type == "TTP":
        mfa_type = "TOTP"

    otp_details = (
        mfa_details.get("otp_details")
        or mfa_details.get("ttp_details")
        or mfa_details.get("otp_max_details")
        or {}
    )

    base = "https://esia.gosuslugi.ru/aas/oauth2/api/login"

    if mfa_type in ("SMS", "TOTP", "MAX"):
        if otp_callback is not None:
            code = (
                await otp_callback(mfa_type, otp_details)
                if asyncio.iscoroutinefunction(otp_callback)
                else otp_callback(mfa_type, otp_details)
            )
        else:
            prompt = "Введите код из SMS: " if mfa_type == "SMS" else "Введите код из приложения: "
            code = input(prompt).strip()

        r = None
        for url in [
            f"{base}/otp/verify",
            f"{base}/totp/verify",
            f"{base}/mfa/verify",
            f"{base}/otp-max/verify",
        ]:
            r = await esia_client.post(url, params={"code": code}, headers=_ESIA_API_HEADERS)
            if r.status_code != 404:
                break

        # Оригинал не принимает 202 — патч это исправляет
        if r.status_code not in (200, 201, 202):
            raise exceptions.MFAError(f"Ошибка подтверждения: {r.status_code} {r.text[:300]}")

        data = r.json()
        if data.get("failed"):
            raise exceptions.MFAError(f"Неверный код: {data['failed']}")

        redirect_url = data.get("redirect_url")
        if redirect_url:
            return redirect_url

        return await self._handle_esia_post_mfa(esia_client, data, otp_callback=otp_callback)

    # PUSH и другие типы — оригинальное поведение
    return await _orig_handle_esia_mfa(self, esia_client, login_data, otp_callback=otp_callback)


async def _patched_handle_esia_post_mfa(self, esia_client, data, otp_callback=None):
    """Патч: убирает проверку skippable у MAX_QUIZ (сервер не возвращает это поле)."""
    base = "https://esia.gosuslugi.ru/aas/oauth2/api/login"

    if not data or not data.get("action"):
        resp = await esia_client.get(f"{base}/next-step", headers=_ESIA_API_HEADERS)
        data = resp.json()

    action = data.get("action", "")

    for _ in range(10):
        if action == "DONE":
            redirect_url = data.get("redirect_url")
            if redirect_url:
                return redirect_url
            raise exceptions.ESIAError("ESIA вернула DONE без redirect_url")

        elif action == "MAX_QUIZ":
            resp = await esia_client.post(
                f"{base}/quiz-max/skip",
                json={},
                headers=_ESIA_API_HEADERS,
            )
            if resp.status_code not in (200, 201, 202):
                raise exceptions.ESIAError(f"Не удалось пропустить MAX_QUIZ (HTTP {resp.status_code})")
            data = resp.json()
            action = data.get("action", "")

        elif action == "CHANGE_PASSWORD":
            resp = await esia_client.post(
                f"{base}/change-password/skip", json={}, headers=_ESIA_API_HEADERS
            )
            if resp.status_code == 200:
                data = resp.json()
                action = data.get("action", "")
            else:
                resp = await esia_client.get(f"{base}/next-step", headers=_ESIA_API_HEADERS)
                data = resp.json()
                action = data.get("action", "")

        else:
            resp = await esia_client.get(f"{base}/next-step", headers=_ESIA_API_HEADERS)
            new_data = resp.json()
            new_action = new_data.get("action", "")
            if new_action == action:
                raise exceptions.ESIAError(f"Неизвестный шаг ESIA: {action}")
            data = new_data
            action = new_action

    raise exceptions.ESIAError("Слишком много шагов ESIA")


async def _patched_esia_finalize_login(
    self, esia_client, sgo_origin, login_state, school, *, timeout=None, user_callback=None
):
    """Патч: переносит куки со всех доменов сервера, а не только с 'sgo'."""
    await esia_client.get(f"{sgo_origin}/webapi/logindata")

    r = await esia_client.get(
        f"{sgo_origin}/webapi/sso/esia/account-info",
        params={"loginState": login_state},
    )
    if r.status_code != 200:
        raise exceptions.ESIAError(f"account-info failed: {r.status_code} {r.text[:200]}")

    account_info = r.json()
    users = account_info.get("users", [])
    if not users:
        raise exceptions.LoginError(
            "Нет привязанных пользователей SGO. "
            "Привяжите аккаунт Госуслуг к Сетевому Городу."
        )

    user = await self._pick_esia_user(users, school, user_callback=user_callback)
    user_id = user["id"]
    roles = user.get("roles", [])
    role = self._pick_parent_role(roles)

    auth_params = {
        "loginType": 8,
        "lscope": user_id,
        "idp": "esia",
        "loginState": login_state,
    }
    if role is not None:
        auth_params["rolegroup"] = role

    r = await esia_client.post(
        f"{sgo_origin}/webapi/auth/login",
        data=auth_params,
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
    )
    if r.status_code != 200:
        raise exceptions.LoginError(f"IDP-логин не удался: {r.status_code} {r.text[:300]}")

    auth_result = r.json()
    at = auth_result.get("at", "")
    if not at:
        raise exceptions.LoginError("SGO не вернул access token (at)")

    self._access_token = at
    self._http.set_header("at", at)

    # Извлекаем хост сервера для фильтрации куки
    from urllib.parse import urlparse
    sgo_host = urlparse(sgo_origin).hostname or ""

    for cookie in esia_client.cookies.jar:
        domain = cookie.domain or ""
        # Переносим куки сервера SGO (по домену) и куки без домена
        if sgo_host in domain or not domain:
            self._http.set_cookie(cookie.name, cookie.value)

    resp = await self._http.get("student/diary/init", timeout=timeout)
    self._init_students(resp.json())

    await self._finish_login(timeout=timeout)
    self._credentials = ()
    self._start_keepalive()


NetSchool._handle_esia_mfa = _patched_handle_esia_mfa
NetSchool._handle_esia_post_mfa = _patched_handle_esia_post_mfa
NetSchool._esia_finalize_login = _patched_esia_finalize_login


async def main():
    ns = NetSchool("https://net-school.cap.ru/")
    await ns.login_via_gosuslugi(
        esia_login=LOGIN,
        esia_password=PASSWORD,
        school=SCHOOL,
    )
    diary = await ns.diary()
    print(diary)
    await ns.logout()


asyncio.run(main())