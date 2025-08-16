"""

"""

from typing import Any, Awaitable, Callable, MutableMapping, ParamSpec, Protocol


## TYPES ##

# all the following is copied from Starlette 
# available in starlette.types as of starlette==0.47.2
P = ParamSpec("P")

ASGIScope = MutableMapping[str, Any]
ASGIMessage = MutableMapping[str, Any]

ASGIReceive = Callable[[], Awaitable[ASGIMessage]]
ASGISend = Callable[[ASGIMessage], Awaitable[None]]
ASGIApp = Callable[[ASGIScope, ASGIReceive, ASGISend], Awaitable[None]]

class _MiddlewareFactory(Protocol[P]):
    def __call__(self, app: ASGIApp, /, *args: P.args, **kwargs: P.kwargs) -> ASGIApp: ... # pragma: no cover

## end TYPES ##

