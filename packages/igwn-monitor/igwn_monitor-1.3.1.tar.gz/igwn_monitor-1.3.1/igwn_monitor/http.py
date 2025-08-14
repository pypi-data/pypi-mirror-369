# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Execute various types of HTTP get."""

from functools import partial
from urllib.parse import urlunparse

import requests
from requests.models import PreparedRequest
from urllib3.util import parse_url

try:
    from requests_gssapi import HTTPSPNEGOAuth
except ModuleNotFoundError:  # debian
    from requests_kerberos import HTTPKerberosAuth as HTTPSPNEGOAuth

from ciecplib import Session
from igwn_auth_utils.requests import (
    HTTPSciTokenAuth,
    SessionAuthMixin as IgwnAuthSessionMixin,
    get as igwn_auth_get,
)
from igwn_auth_utils.scitokens import target_audience
from requests_ecp import HTTPECPAuth

from .auth import DEFAULT_IDP
from .compat import nullcontext

# set conservative default timeout to prevent request hanging
DEFAULT_REQUEST_TIMEOUT = 60

# list of ports to be considered HTTP (not HTTPS)
HTTP_PORTS = [
    80,
    591,  # IANA HTTP alternative
    8000,  # XRootD over HTTP
    8008,  # IANA HTTP alternative
    8080,  # IANA HTTP alternative
]

# keywords for various auth types
KERBEROS_KW = {
    "kerberos_kdc",
    "kerberos_keytab",
    "kerberos_principal",
}
SCITOKEN_KW = {
    "token_audience",
    "token_issuer",
    "token_scope",
    "token_vaultserver",
    "token_vaulttokenfile",
    "token_credkey",
    "token_role",
}
SESSION_KW = {
    # generic kwargs
    "auth",
    # ciecplib kwargs
    "cookiejar",
    "debug",
    "idp",
    "kerberos",
    "password",
    "username",
    # igwn-auth-utils kwargs
    "cert",
    "token",
    "token_audience",
    "token_scope",
}
X509_KW = {
    "idp",
    "proxy",
}


# -- utilities --------------

def make_url(
    host,
    *paths,
    scheme=None,
    port=None,
    query=None,
    fragment=None,
):
    """Construct a fully-qualified URL from a hostname and path.

    Parameters
    ----------
    host : `str`
        Name or URL of host, optionally including a port number.

    paths : `str`
        Zero or more path components to append to the full URL.

    scheme : `str`
        The scheme to use if not included in the ``host``.
        If ``host`` specifies port 80, this defaults to ``"http"``,
        otherwise ``"https"``.

    port : `int`
        The port to use if not included in the ``host``.
        Default is to not include a port number.

    query : `str`, `dict`
        A query string or `dict` of params to include in the full URL.

    fragment : `str`
        A URL fragment to include in the full URL.

    Returns
    -------
    url : `str`
        A fully-qualified URL.

    Examples
    --------
    >>> make_url('example.com')
    'https://example.com'
    >>> make_url('datafind.example.com:80', '/LDR', 'api/version')
    'http://datafind.example.com:80/LDR/api/version
    """
    # parse host to determine scheme
    parsed = parse_url(host)
    if parsed.scheme is None and scheme is None and parsed.port in HTTP_PORTS:
        scheme = "http"
    elif parsed.scheme is None and scheme is None:
        scheme = "https"
    elif parsed.scheme is not None:
        scheme = parsed.scheme

    # if host didn't include a port, but the user did, use that
    netloc = parsed.netloc
    if parsed.port is None and port is not None:
        netloc += f":{port}"

    # if host actually included paths, preserve those
    if parsed.path:
        paths = (parsed.path,) + paths

    # combine paths in a normalised way
    if paths:
        path = "/".join(x.strip("/") for x in paths)
        if paths[-1].endswith("/"):  # reinstate trailing slash
            path += "/"
    else:
        path = "/"

    # then join it up using requests to format a query
    return urlunparse((
        scheme,
        netloc,
        path,
        None,
        PreparedRequest._encode_params(query),
        fragment,
    ))


def handle_response(resp):
    """Handle a response from a URL.

    Just executes the `raise_for_status` method of the response object.
    """
    resp.raise_for_status()
    return resp


def response_message(r):
    """Return a Nagios status message for a response.

    e.g. ``"'200 OK' from https://example.com"``
    """
    return f"'{r.status_code} {r.reason}' from {r.request.url}"


def response_performance(
    response,
    warning_time=None,
    critical_time=None,
):
    """Return performance metrics for a request.

    Parameters
    ----------
    response : `requests.Response`
        the response object to parse.

    warning_time : `float`, `None`
        time (in seconds) above which a `response_time` should be considered
        WARNING.

    critical_time : `float`, `None`
        time (in seconds) above which a `response_time` should be considered
        CRITICAL.
    """
    return {
        "response_time": (
            f"{response.elapsed.total_seconds()}s",
            warning_time,
            critical_time,
            0,  # minimum value
            None,  # maximum value
        ),
    }


# -- Omni auth handler ------

class IgwnOmniAuth(HTTPSciTokenAuth, HTTPECPAuth, HTTPSPNEGOAuth):
    def __init__(
        self,
        *args,
        idp=DEFAULT_IDP,
        kerberos=False,
        username=None,
        password=None,
        token=None,
        **spnego_kw,
    ):
        if idp in ("login.ligo.org", "login2.ligo.org"):
            idp = f"https://{idp}/idp/profile/SAML2/SOAP/ECP"
        HTTPECPAuth.__init__(
            self,
            idp,
            kerberos=kerberos,
            username=username,
            password=password,
        )

        HTTPSciTokenAuth.__init__(
            self,
            token=token,
        )

        HTTPSPNEGOAuth.__init__(self, **spnego_kw)

    def handle_response_spnego(self, response, **kwargs):
        return HTTPSPNEGOAuth.handle_response(self, response, **kwargs)

    def __call__(self, request):
        for parent in (
            HTTPSciTokenAuth,
            HTTPECPAuth,
            HTTPSPNEGOAuth,
        ):
            request = parent.__call__(self, request)

        # the registered hooks don't get registered properly because
        # the handlers in the different classes have the same name
        # so, manually reregister hook for SPNEGO since it comes last
        request.register_hook("response", self.handle_response_spnego)

        # and then clean up duplicate registerations
        request.hooks["response"] = list(set(request.hooks["response"]))

        return request


class IgwnOmniAuthSession(IgwnAuthSessionMixin, Session):
    pass


# -- request preparation ----

def _pop_kwargs(kwargs, keys, prefix=None):
    """Extract entries from a dict matching a list of keys, stripping a prefix
    out along the way.
    """
    n = len(prefix) if prefix else 0
    return {key[n:]: kwargs.pop(key) for key in keys if key in kwargs}


def prepare_kerberos(kwargs):
    """Handle keywords for Kerberos usage and return a
    `igwn_monitor.auth.kerberos_tgt` context manager.
    """
    kerberos = kwargs.get("kerberos", None)
    if kerberos is not False:
        from .auth import kerberos_tgt
        kerberos_kw = _pop_kwargs(kwargs, KERBEROS_KW, prefix="kerberos_")
        return kerberos_tgt(**kerberos_kw)
    return nullcontext()


def prepare_scitoken(url, kwargs):
    """Handle keywords for SciToken usage and return a
    `igwn_monitor.auth.scitoken` context manager.
    """
    from .auth import scitoken
    if kwargs.get("token_audience", None) is None:
        kwargs["token_audience"] = target_audience(url, include_any=False)

    token_kw = {
        "kerberos": kwargs.pop("kerberos", True),
        "strict": kwargs.pop("strict", True),
    }
    token_kw.update(_pop_kwargs(kwargs, SCITOKEN_KW, prefix="token_"))
    token_kw.update(_pop_kwargs(kwargs, KERBEROS_KW, prefix="kerberos_"))

    return scitoken(**token_kw)


def prepare_x509(kwargs):
    """Handle keywords for X.509 usage and return a
    `igwn_monitor.auth.x509` context manager.
    """
    from .auth import x509
    x509_kw = _pop_kwargs(kwargs, X509_KW | {"kerberos", "strict"})
    x509_kw.update(_pop_kwargs(kwargs, KERBEROS_KW, prefix="kerberos_"))
    return x509(**x509_kw)


def prepare_session(kwargs):
    """Handle keywords for a Session and return one."""
    session_class = kwargs.pop("session_class", Session)
    session_kw = _pop_kwargs(kwargs, SESSION_KW)

    # remove one unnecessary request
    idp = session_kw.get("idp", None)
    if idp in ("login.ligo.org", "login2.ligo.org"):
        session_kw["idp"] = f"https://{idp}/idp/profile/SAML2/SOAP/ECP"

    # remove unsupported kwargs
    for key in (
        "token_vaultserver",
        "token_vaulttokenfile",
    ):
        kwargs.pop(key, None)

    return session_class(**session_kw)


# -- GET methods ------------

def get_no_auth(url, timeout=DEFAULT_REQUEST_TIMEOUT, **request_kw):
    """GET a URL with no authentication."""
    # remove credentials only used for authorisation
    for kwlist in (
        KERBEROS_KW,
        SCITOKEN_KW,
        SESSION_KW,
        X509_KW,
    ):
        _pop_kwargs(request_kw, kwlist)

    return requests.get(
        url,
        auth=None,
        cert=None,
        timeout=timeout,
        **request_kw,
    )


def get_with_saml(
    url,
    timeout=DEFAULT_REQUEST_TIMEOUT,
    **request_kw,
):
    """GET a URL with SAML (ECP) authentication."""
    request_kw.setdefault("idp", DEFAULT_IDP)
    kerberos_ctx = prepare_kerberos(request_kw)
    session_ctx = prepare_session(request_kw)

    with kerberos_ctx, session_ctx as sess:
        resp = sess.get(
            url,
            timeout=timeout,
            **request_kw,
        )
        resp.cookies.update(sess.cookies)
        return resp


def get_with_kerberos(
    url,
    timeout=DEFAULT_REQUEST_TIMEOUT,
    **request_kw,
):
    """GET a URL with Kerberos (SPNEGO) authentication."""
    _pop_kwargs(request_kw, SESSION_KW)
    _pop_kwargs(request_kw, X509_KW)
    with prepare_kerberos(request_kw):
        request_kw.pop("kerberos", None)
        return requests.get(
            url,
            auth=HTTPSPNEGOAuth(),
            timeout=timeout,
            **request_kw,
        )


def get_with_x509(
    url,
    timeout=DEFAULT_REQUEST_TIMEOUT,
    **request_kw,
):
    """GET a URL with X.509 authentication."""
    _pop_kwargs(request_kw, SCITOKEN_KW)
    with prepare_x509(request_kw):
        return igwn_auth_get(
            url,
            cert=True,
            token=False,
            timeout=timeout,
            **request_kw,
        )


def get_with_scitoken(
    url,
    timeout=DEFAULT_REQUEST_TIMEOUT,
    **request_kw,
):
    """GET a URL with bearer token (SciToken) authentication.

    This is (mostly) unfinished, and will only work with existing
    externally-created scitokens.
    """
    # ignore some kwargs that are used for other auth types
    _pop_kwargs(request_kw, X509_KW)

    # create a token and make the request via igwn_auth_utils
    with prepare_scitoken(url, request_kw) as token:
        return igwn_auth_get(
            url,
            cert=False,
            token=token,
            timeout=timeout,
            **request_kw,
        )


def get_with_any(
    url,
    timeout=DEFAULT_REQUEST_TIMEOUT,
    **request_kw,
):
    """GET a URL trying all types of Authorisation at the same time."""
    # get a kerberos ticket
    request_kw.setdefault("idp", DEFAULT_IDP)
    with prepare_kerberos(request_kw):
        # don't redo kerberos
        kerberos = request_kw.setdefault("kerberos", False)

        # don't fail hard if creds don't work out
        strict = request_kw.setdefault("strict", False)

        # get a token
        token_ctx = prepare_scitoken(url, request_kw)

        # reset params for X.509 incase 'pop'ped when preparing the token
        request_kw.setdefault("kerberos", kerberos)
        request_kw.setdefault("strict", strict)

        # get X.509
        x509_ctx = prepare_x509(request_kw)

        # get a token AND an X.509 credential
        with token_ctx as token, x509_ctx:
            # open an OmniAuth session
            request_kw["auth"] = IgwnOmniAuth(
                idp=request_kw.pop("idp", DEFAULT_IDP),
                kerberos=request_kw.get("kerberos", True),
                token=token or False,  # if token is None, don't use any other
            )
            request_kw.setdefault("session_class", IgwnOmniAuthSession)
            with prepare_session(request_kw) as sess:
                # finally make the request
                resp = sess.get(
                    url,
                    timeout=timeout,
                    **request_kw,
                )
                resp.cookies.update(sess.cookies)
                return resp


AUTH_GET_FUNCTIONS = {
    "none": get_no_auth,
    "saml": get_with_saml,
    "kerberos": get_with_kerberos,
    "x509": get_with_x509,
    "x509_proxy": partial(get_with_x509, proxy=True),
    "scitoken": get_with_scitoken,
    "any": get_with_any,
}


def get_with_auth(auth_type, url, **request_kw):
    """Wrapper to call the correct auth ``get`` method."""
    # find the right getter
    get = AUTH_GET_FUNCTIONS[auth_type]

    # sanitise kwargs
    if auth_type not in {"any", "scitoken"}:
        _pop_kwargs(request_kw, SCITOKEN_KW)

    # get and return
    return get(url, **request_kw)
