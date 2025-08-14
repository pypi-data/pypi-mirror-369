#    Copyright 2025 Genesis Corporation.
#
#    All Rights Reserved.
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

from restalchemy.api import routes

from genesis_notification.user_api.api import controllers


class ProviderRoute(routes.Route):
    __controller__ = controllers.ProviderController


class TemplateRoute(routes.Route):
    __controller__ = controllers.TemplateController


class EventTypeRoute(routes.Route):
    __controller__ = controllers.EventTypeController


class EventRoute(routes.Route):
    __controller__ = controllers.EventController


class ApiEndpointRoute(routes.Route):
    """Handler for /v1.0/ endpoint"""

    __controller__ = controllers.ApiEndpointController
    __allow_methods__ = [routes.FILTER]

    providers = routes.route(ProviderRoute)
    templates = routes.route(TemplateRoute)
    event_types = routes.route(EventTypeRoute)
    events = routes.route(EventRoute)
