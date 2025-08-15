# -*- coding: utf-8 -*-
"""
Exceptions
"""

class ServerAuthError(Exception):
    def __init__(
        self,
    ) -> None:
        super().__init__("Server Auth Error, check the password.")


class AddressError(Exception):
    def __init__(
        self,
    ) -> None:
        super().__init__("IP address and PORT is incorrect.")


class PasswordError(Exception):
    def __init__(
        self,
    ) -> None:
        super().__init__("Password has not been provided or is incorrect.")
