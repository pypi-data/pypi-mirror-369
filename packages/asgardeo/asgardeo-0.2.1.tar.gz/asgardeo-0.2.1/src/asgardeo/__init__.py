"""
Copyright (c) 2025, WSO2 LLC. (https://www.wso2.com).
WSO2 LLC. licenses this file to you under the Apache License,
Version 2.0 (the "License"); you may not use this file except
in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.
"""

from .auth import AsgardeoNativeAuthClient, AsgardeoTokenClient
from .models import (
    AsgardeoConfig,
    AsgardeoError,
    AuthenticationError,
    FlowStatus,
    NetworkError,
    OAuthToken,
    TokenError,
    ValidationError,
)
from .auth.util import generate_pkce_pair, generate_state, build_authorization_url

__version__ = "0.2.1"

__all__ = [
    "AsgardeoConfig",
    "AsgardeoError",
    "AsgardeoNativeAuthClient",
    "AsgardeoTokenClient",
    "AuthenticationError",
    "FlowStatus",
    "NetworkError",
    "OAuthToken",
    "TokenError",
    "ValidationError",
    "generate_pkce_pair",
    "generate_state",
    "build_authorization_url",
]
