# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains permission checking decorators for wrapping pecan request handler methods.
"""

from functools import wraps

import pecan

from st2common.rbac import utils

__all__ = [
    'request_user_is_admin',
    'request_user_has_permission',
    'request_user_has_resource_permission'
]


def request_user_is_admin():
    def decorate(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            utils.assert_request_user_is_admin(request=pecan.request)
            return func(*args, **kwargs)
        return func_wrapper
    return decorate


def request_user_has_permission(permission_type):
    def decorate(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            utils.assert_request_user_has_permission(request=pecan.request,
                                                     permission_type=permission_type)
            return func(*args, **kwargs)
        return func_wrapper
    return decorate


def request_user_has_resource_permission(permission_type):
    """
    A decorator meant to wrap post, put and delete Pecan REST controller methods.

    This decorator assumes the first argument passed to the decorated function is a resource
    reference or an ID.

    Internally, this decorator retrieves the object from the DB so it can perform the permission
    checking.

    Note: The same query happens inside the decorator function meaning this is not the most
    efficient approach and we should eventually cache the "get one" results.
    """
    def decorate(func):
        function_name = func.__name__
        if function_name not in ['post', 'put', 'delete']:
            raise Exception('This decorator should only be used to wrap post, put and delete '
                            'methods')

        @wraps(func)
        def func_wrapper(*args, **kwargs):
            controller_instance = args[0]
            resource_ref_or_id = args[1]

            # TODO: Special case for key value pair controller - use "_get_one_raw"
            resource_db = controller_instance._get_by_ref_or_id(ref_or_id=resource_ref_or_id)
            utils.assert_request_user_has_resource_permission(request=pecan.request,
                                                              resource_db=resource_db,
                                                              permission_type=permission_type)
            return func(*args, **kwargs)
        return func_wrapper
    return decorate
