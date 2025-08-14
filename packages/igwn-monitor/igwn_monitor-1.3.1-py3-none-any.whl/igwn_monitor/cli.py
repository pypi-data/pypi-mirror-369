# Copyright (c) 2023-2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Command-line utilities for IGWN monitors."""

import argparse
import os
from pathlib import Path

from . import __version__
from .auth import (
    DEFAULT_IDP,
    DEFAULT_TOKEN_ISSUER,
    DEFAULT_VAULT,
)
from .http import (
    AUTH_GET_FUNCTIONS,
    DEFAULT_REQUEST_TIMEOUT,
)


class IgwnMonitorArgumentFormatter(
    argparse.RawDescriptionHelpFormatter,
    argparse.ArgumentDefaultsHelpFormatter,
):
    pass


class IgwnMonitorArgumentParser(argparse.ArgumentParser):
    def __init__(
        self,
        *args,
        add_version=True,
        add_timeout=True,
        add_output_options=True,
        **kwargs,
    ):
        kwargs.setdefault("formatter_class", IgwnMonitorArgumentFormatter)
        super().__init__(*args, **kwargs)
        self._positionals.title = "Positional arguments"
        self._optionals.title = "Optional arguments"

        # add a default `--version` argument
        if add_version:
            self.add_version()

        # add a default `--timeout` argument
        if add_timeout:
            if add_timeout is True:
                timeout = DEFAULT_REQUEST_TIMEOUT
            else:  # user-specified value
                timeout = float(add_timeout)
            self.add_timeout(default=timeout)

        # add a default `--output-file` argument
        if add_output_options:
            self.add_output_argument_group()

    def add_timeout(
        self,
        default=DEFAULT_REQUEST_TIMEOUT,
        help="seconds before check times out",
        **kwargs,
    ):
        """Add a ``-t/--timeout`` argument to this `ArgumentParser`."""
        self.add_argument(
            "-t",
            "--timeout",
            type=float,
            default=default,
            help=help,
            **kwargs,
        )

    def add_version(self):
        """Add a ``-V/--version`` argument to this `ArgumentParser`."""
        self.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"{self.prog} {__version__}",
        )

    def add_output_argument_group(
        self,
        title="Output options",
        description=None,
    ):
        """Add output options to this `ArgumentParser`."""
        group = self.add_argument_group(
            title=title,
            description=None,
        )
        group.add_argument(
            "-O",
            "--output-file",
            action="store",
            default="stdout",
            help="path of file to write to",
        )
        group.add_argument(
            "-J",
            "--output-json-expiry",
            action="store",
            type=int,
            default=None,
            help=(
                "time (seconds) after which JSON output report should be "
                "marked as invalid"
            ),
        )
        return group

    def add_auth_argument_group(
        self,
        title="Authorisation arguments",
        auth_type="none",
        kerberos=True,
        description=None,
        keytab=True,
        principal=True,
        scitoken=True,
    ):
        """Add authentication/authorisation arguments to this `ArgumentParser`.

        Parameters
        ----------
        title : `str`
            The title for this argument group.

        description : `str`
            The description for this argument group.

        auth_type : `str`, `list`
            The default authorisation type to use. If a `list` (or `tuple`)
            is given, use the first element as the default, and only accept
            items from the given iterable as valid choices.

        kerberos : `bool`
            If `True` enable Kerberos auth by default, and add a
            `--no-kerberos` to disable it. If `False`, add a `--kerberos`
            option to enable it.

        principal : `bool`
            If `True` (default) add the `-P/--kerberos-principal` argument.

        scitoken : `bool`
            If `True` (default) add a number of SciToken-related arguments.
        """
        if isinstance(auth_type, (list, tuple)):
            auth_choices = auth_type
            auth_type = auth_type[0]
        else:
            auth_choices = AUTH_GET_FUNCTIONS.keys()

        group = self.add_argument_group(
            title=title,
            description=description,
        )
        group.add_argument(
            "-a",
            "--auth-type",
            choices=auth_choices,
            default=auth_type,
            help="auth type to use",
        )
        if {"saml", "x509", "x509_proxy", "any"}.intersection(auth_choices):
            group.add_argument(
                "-i",
                "--identity-provider",
                default=DEFAULT_IDP,
                help="name of ECP Identity Provider",
            )
        if kerberos:
            group.add_argument(
                "-K",
                "--no-kerberos",
                dest="kerberos",
                default=True,
                action="store_false",
                help="Disable kerberos auth",
            )
        else:
            group.add_argument(
                "-k",
                "--kerberos",
                action="store_true",
                help="Use Kerberos auth",
            )
        if keytab:
            group.add_argument(
                "-B",
                "--kerberos-keytab",
                default=os.getenv("KRB5_KTNAME"),
                type=Path,
                help="path to Kerberos keytab file",
            )
        if principal:
            group.add_argument(
                "-P",
                "--kerberos-principal",
                help=(
                    "principal to use with Kerberos, auto-discovered from "
                    "-K/--kerberos-keytab if given"
                ),
            )
        if scitoken:
            group.add_argument(
                "-X",
                "--token-vaultserver",
                default=DEFAULT_VAULT,
                help="URL of token vault server",
            )
            group.add_argument(
                "-I",
                "--token-issuer",
                default=DEFAULT_TOKEN_ISSUER,
                help="name of token issuer",
            )
            group.add_argument(
                "-G",
                "--token-vaulttokenfile",
                help="path of vault token to read/write",
            )
            group.add_argument(
                "-T",
                "--token-audience",
                help=(
                    "audience for scitoken, defaults to the fully-qualified "
                    "URL of the target host"
                ),
            )
            group.add_argument(
                "-S",
                "--token-scope",
                help="scope (or comma-separated list) for scitoken",
            )
            group.add_argument(
                "-R",
                "--token-role",
                help="vault name of role for OIDC",
            )
            group.add_argument(
                "-C",
                "--token-credkey",
                help="key to use in vault secretpath"
            )
        return group
