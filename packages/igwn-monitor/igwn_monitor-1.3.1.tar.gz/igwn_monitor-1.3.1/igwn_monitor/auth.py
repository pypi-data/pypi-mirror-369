# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Auth credential utilities for IGWN monitors."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import os
import subprocess
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from string import Template
from tempfile import TemporaryDirectory
from time import sleep
from unittest.mock import patch

from .compat import nullcontext

DEFAULT_IDP = os.getenv("ECP_IDP") or "login.ligo.org"
DEFAULT_TOKEN_ISSUER = "igwn"  # noqa: S105
DEFAULT_VAULT = "vault.ligo.org"

# -- Kerberos -------------------------

KRB5_CONF = Template("""
[libdefaults]
default_realm = $realm
default_ccache_name = $ccache
[realms]
$realm = {
kdc = $kdc
}
[appdefaults]
krb4_get_tickets = false
""")


def write_krb5_config(path, kdc, realm, ccache):
    """Write a ``krb5.conf`` file to the given path."""
    path = Path(path)
    conf = KRB5_CONF.substitute(
        ccache=ccache,
        kdc=kdc,
        realm=realm,
    ).strip()
    with path.open("w") as file:
        file.write(conf)
    return path


def _default_gssapi_principal(ccache=None, keytab=None):
    """Find the default Kerberos principal, specific to a keytab (if given).

    Raises
    ------
    ValueError
        If no default principal could be found (either no ``keytab`` was
        given, or no existing credential is active).
    """
    kw = {}
    if keytab:
        kw["client_keytab"] = str(keytab)
    if ccache:
        kw["ccache"] = str(ccache)
    creds = _existing_gssapi_creds(lifetime=0, **kw)
    if creds:
        return creds.name
    msg = "failed to identify default Kerberos principal"
    raise ValueError(msg)


def _existing_gssapi_creds(name=None, lifetime=1, **store):
    """Find existing Kerberos credentials."""
    import gssapi

    if store.get("client_keytab"):
        # usage=initiate with a keytab will create new creds
        # if needed, which we don't want _here_
        usage = "accept"
    else:
        usage = "initiate"

    try:
        creds = gssapi.Credentials(
            name=name,
            usage=usage,
            store=store,
        )

        if creds is None:
            return None

        # if we weren't asked for a lifetime, we're just looking for the creds
        if not lifetime:
            return creds

        # otherwise we need real creds, so attempt to acquire them
        if creds.lifetime is None:
            creds = creds.acquire().creds

        # now assert that they are within the lifetime
        if creds.lifetime >= lifetime:
            return creds
    except gssapi.exceptions.GSSError:
        return None


def _kinit(
    principal,
    keytab=None,
    ccache=None,
):
    """Initialise a new GSSAPI (Kerberos) credential."""
    import gssapi
    store_kw = {}
    if keytab:
        store_kw["client_keytab"] = str(keytab)
    if ccache:
        store_kw["ccache"] = str(ccache)
    creds = gssapi.Credentials(
        name=principal,
        usage="initiate",
        store=store_kw,
    )
    try:
        creds.inquire()
    except gssapi.raw.exceptions.ExpiredCredentialsError:
        creds.acquire()
    return creds


@contextmanager
def kerberos_tgt(
    principal=None,
    ccache=None,
    kdc=None,
    keytab=None,
    force=False,
):
    """Context manager to create a new Kerberos TGT.

    If existing GSSAPI credentials are discovered matching the principal,
    these will be returned, unless ``force=True`` is given.
    """
    import gssapi

    kstore = {}

    # get default keytab from the environment
    if keytab is None:
        keytab = os.getenv("KRB5_KTNAME") or None
    if keytab:
        keytab = kstore["client_keytab"] = str(keytab)

    # get default credential cache from the environment
    if ccache is None:
        ccache = os.getenv("KRB5CCNAME") or None
    if ccache:
        ccache = kstore["ccache"] = str(ccache)

    # find default principal (using the given keytab)
    if principal is None:
        principal = _default_gssapi_principal(
            ccache=ccache,
            keytab=keytab,
        )
    else:
        principal = gssapi.Name(
            principal,
            name_type=gssapi.NameType.kerberos_principal,
        )

    # if not forced to get new creds, try and use existing creds
    creds = _existing_gssapi_creds(name=principal, lifetime=10, **kstore)
    if not force and creds is not None:
        yield creds
        return

    # create a new credential using a temporary credential configuration
    with TemporaryDirectory() as tmpdir, patch.dict("os.environ"):
        tmpdir = Path(tmpdir)

        if keytab:  # overwrite the environmeny keytab (just in case)
            os.environ["KRB5_KTNAME"] = keytab = str(keytab)

        if ccache is None:  # use a temporary credential cache
            ccache = tmpdir / "ccache"
        os.environ["KRB5CCNAME"] = ccache = str(ccache)

        if kdc:
            # write kerberos config to point only at the given KDC
            krbconf = write_krb5_config(
                tmpdir / "krb5.conf",
                ccache=ccache,
                kdc=kdc,
                realm=str(principal).split("@", 1)[1],
            )
            os.environ["KRB5_CONFIG"] = str(krbconf)

        # get the new creds
        yield _kinit(
            principal,
            keytab=keytab,
            ccache=ccache,
        )


@contextmanager
def x509(
    idp=DEFAULT_IDP,
    hours=1,
    force=False,
    proxy=None,
    kerberos=True,
    strict=True,
    **kerberos_kw,
):
    """Context manager to create a new X.509 credential.

    If an existing credential is discovered that meets the requirements, that
    will be used, unless ``force=True`` is given.
    """
    from ciecplib.x509 import (
        _cert_type as cert_type,
        load_cert as load_x509,
    )
    from igwn_auth_utils import find_x509_credentials

    if not force:  # check for existing credentials
        try:
            creds = find_x509_credentials(timeleft=hours * 3600)
        except RuntimeError:
            pass
        else:
            # if we have some, use them
            if isinstance(creds, tuple):
                creds = creds[0]
            creds = load_x509(creds)
            ctype = cert_type(creds).lower()
            if (
                proxy is None
                or (proxy and "proxy" in ctype)
                or (not proxy and ctype == "end entity credential")
            ):
                yield creds
                return

    # prepare a kerberos credential, unless told not to
    if kerberos:
        krb_ctx = kerberos_tgt(**kerberos_kw)
    else:
        krb_ctx = nullcontext()

    # get a new credential and store in a temporary directory
    with krb_ctx, TemporaryDirectory() as tmpdir, patch.dict("os.environ"):
        from ciecplib.ui import get_cert as get_x509
        from ciecplib.x509 import write_cert as write_x509

        tmpdir = Path(tmpdir)

        # remove one unnecessary external request
        if idp in ("login.ligo.org", "login2.ligo.org"):
            idp = f"https://{idp}/idp/profile/SAML2/SOAP/ECP"

        # get a new certificate
        try:
            cert, key = get_x509(
                endpoint=idp,
                kerberos=True,
                hours=hours,
            )
        except Exception:
            if not strict:
                yield
                return
            raise

        # store it in a file
        os.environ["X509_USER_PROXY"] = certfile = str(tmpdir / "x509.pem")
        write_x509(certfile, cert, key, use_proxy=proxy, minhours=hours)

        yield cert


x509_proxy = partial(x509, proxy=True)


@contextmanager
def scitoken(
    vaultserver=DEFAULT_VAULT,
    issuer=DEFAULT_TOKEN_ISSUER,
    vaulttokenfile=None,
    audience=None,
    scope=None,
    role=None,
    credkey=None,
    force=False,
    kerberos=True,
    strict=True,
    timeout=120,
    **kerberos_kw,
):
    """Context manager to create a new SciToken.

    If an existing token is discovered that meets the requirements, that
    will be used, unless ``force=True`` is given.
    """
    from igwn_auth_utils.scitokens import (
        deserialize_token,
        find_token,
    )

    # format arguments
    if isinstance(scope, str):
        scope = scope.split(",")
    if isinstance(audience, str):
        audience = audience.split(",")

    if not force:  # check for existing credentials
        try:
            token = find_token(
                audience,
                scope,
                timeleft=60,
            )
        except Exception:
            pass
        else:
            yield token
            return

    # prepare a kerberos credential, unless told not to
    if kerberos:
        krb_ctx = kerberos_tgt(**kerberos_kw)
    else:
        krb_ctx = nullcontext()

    # get a new credential and store in a temporary directory
    with krb_ctx, TemporaryDirectory() as tmpdir, patch.dict("os.environ"):
        tmpdir = Path(tmpdir)
        btpath = tmpdir / "bt"

        # get token
        cmd = [
            "htgettoken",
            "--vaultserver", vaultserver,
            "--issuer", issuer,
            "--outfile", str(btpath),
            "--nooidc",
        ]
        if vaulttokenfile:
            cmd.extend(("--vaulttokenfile", str(vaulttokenfile)))
        if audience:
            cmd.extend(("--audience", ",".join(audience)))
        if scope:
            cmd.extend(("--scopes", ",".join(scope)))
        if role:
            cmd.extend(("--role", str(role)))
        if credkey:
            cmd.extend(("--credkey", str(credkey)))
        try:
            subprocess.run(  # noqa: S603
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if not strict else None,
                timeout=timeout,
            )
        except subprocess.SubprocessError:
            if not strict:  # ignore error, return None
                yield
                return
            raise
        sleep(1)

        # load token
        with open(btpath, "r") as file:
            raw = file.read()
        token = deserialize_token(raw)

        # validate that the token has the scopes that were requested
        if scope is not None and not _validate_token_scopes(
            token,
            audience,
            scope,
            strict=strict,
        ):
            yield
            return

        # seed the environment
        os.environ["BEARER_TOKEN_FILE"] = str(btpath)
        with open(btpath, "r"):
            os.environ["BEARER_TOKEN"] = raw

        yield token


def _validate_token_scopes(token, audiences, scopes, strict=True):
    """Validate a SciToken has the scopes that were requested.

    This function may become redundant when the token issuer starts
    returning an error code for invalid/missing scopes.

    Returns
    -------
    valid : `bool`
        `True` if the token is valid and contains all of the
        requested scopes, `False` otherwise (if ``strict=False``).

    Raises
    ------
    scitokens.scitokens.ClaimInvalid
        If ``strict=True`` and the token fails the enforcement test.
    """
    from scitokens import Enforcer
    from scitokens.scitokens import ClaimInvalid

    enforcer = Enforcer(
        # use the token's issuer, we aren't validating that
        token["iss"],
        # use any audience that won't confuse the enforcer
        # NOTE: if 'audiences' is None, then the token will have aud=ANY
        #       so we just have to use anything that _isn't_ ANY to validate
        audience=audiences[0] if audiences else "audience",
    )
    for scope in scopes:
        try:
            authz, path = scope.split(":", 1)
        except ValueError:
            authz = scope
            path = None
        if enforcer.test(token, authz, path=path):
            continue
        reason = enforcer.last_failure
        if strict:
            raise ClaimInvalid(reason)
        return False
    return True


# -- generic context ------------------

AUTH_CONTEXT = {
    "kerberos": kerberos_tgt,
    "scitoken": scitoken,
    "x509": x509,
    "x509_proxy": x509_proxy,
}


def auth_context(
    auth_type=None,
    **auth_kw,
):
    """Create an auth context.

    This is just a convenience wrapper to handle accepting arguments
    from the command line and parsing them into an authorisation context
    manager.
    """
    if auth_type in (None, "none"):
        return nullcontext()

    # sanitise keywords
    for key in list(auth_kw):
        if (
            (auth_type != "scitoken" and key.startswith("token_"))
            or (not auth_type.startswith("x509") and key == "idp")
        ):
            auth_kw.pop(key)
        elif key.startswith(("kerberos_", "token_")):
            auth_kw[key.split("_", 1)[-1]] = auth_kw.pop(key)

    return AUTH_CONTEXT[auth_type](**auth_kw)
