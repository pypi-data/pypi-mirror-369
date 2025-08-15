# Copyright 2018 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


class FishyError(Exception):
    """Create generic sushy-tools exception object"""

    def __init__(self, msg='Unknown error', code=500):
        super().__init__(msg)
        self.code = code


class AliasAccessError(FishyError):
    """Node access attempted via an alias, not UUID"""


class NotSupportedError(FishyError):
    """Feature not supported by resource driver"""

    def __init__(self, msg='Unsupported', code=501):
        super().__init__(msg, code)


class NotFound(FishyError):
    """Entity not found."""

    def __init__(self, msg='Not found', code=404):
        super().__init__(msg, code)


class BadRequest(FishyError):
    """Malformed request."""

    def __init__(self, msg, code=400):
        super().__init__(msg, code)


class FeatureNotAvailable(NotFound):
    """Feature is not available."""

    def __init__(self, feature, code=404):
        super().__init__(f"Feature {feature} not available", code=code)


class Conflict(FishyError):
    """Conflict with current state of the resource."""

    def __init__(self, msg, code=409):
        super().__init__(msg, code)


class ConfigInvalid(FishyError):
    """Config is invalid."""

    def __init__(self, msg, code=500):
        errmsg = f"Invalid configuration file. {msg}"
        super().__init__(errmsg, code)


class Unauthorized(FishyError):
    """Unauthorized for resource"""

    def __init__(self, msg, code=401):
        self.headers = {'WWW-Authenticate': 'Basic realm="Baremetal API"'}
        super().__init__(msg, code)
