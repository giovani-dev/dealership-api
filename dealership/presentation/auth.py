import functools
from typing import List

from flask import jsonify, request

from dealership.core.facade import AuthFacade


def claims(_claims: List[str]):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(claims=_claims, *args, **kwargs):
            header = [
                header
                for header in list(request.headers)
                if header[0] == "Authorization"
            ]
            try:
                header = header[0][1]
            except Exception:
                header = None
            auth = AuthFacade(data={"Authorization": header})
            callback = await auth.verify(claims)
            if callback.status_code.value >= 400:
                try:
                    return jsonify(callback.content.dict()), callback.status_code.value
                except AttributeError:
                    return jsonify(callback.content), callback.status_code.value
            setattr(request, "user", callback.content)
            return await func(*args, **kwargs)

        return wrapper

    return decorator
