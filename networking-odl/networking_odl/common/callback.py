# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

import collections

from oslo_log import log as logging

from neutron.callbacks import events
from neutron.callbacks import registry
from neutron.callbacks import resources

from networking_odl.common import constants as odl_const

LOG = logging.getLogger(__name__)

ODLResource = collections.namedtuple('ODLResource', ('singular', 'plural'))
_RESOURCE_MAPPING = {
    resources.SECURITY_GROUP: ODLResource(odl_const.ODL_SG, odl_const.ODL_SGS),
    resources.SECURITY_GROUP_RULE: ODLResource(odl_const.ODL_SG_RULE,
                                               odl_const.ODL_SG_RULES),
}
_OPERATION_MAPPING = {
    events.AFTER_CREATE: odl_const.ODL_CREATE,
    events.AFTER_UPDATE: odl_const.ODL_UPDATE,
    events.AFTER_DELETE: odl_const.ODL_DELETE,
}


class OdlSecurityGroupsHandler(object):

    def __init__(self, odl_driver):
        self.odl_driver = odl_driver
        self._subscribe()

    def _subscribe(self):
        for event in (events.AFTER_CREATE, events.AFTER_DELETE):
            registry.subscribe(self.sg_callback, resources.SECURITY_GROUP,
                               event)
            registry.subscribe(self.sg_callback, resources.SECURITY_GROUP_RULE,
                               event)

        registry.subscribe(self.sg_callback, resources.SECURITY_GROUP,
                           events.AFTER_UPDATE)

    def sg_callback(self, resource, event, trigger, **kwargs):
        res = kwargs.get(resource)
        res_id = kwargs.get("%s_id" % resource)
        odl_res_type = _RESOURCE_MAPPING[resource]

        odl_ops = _OPERATION_MAPPING[event]
        odl_res_dict = None if res is None else {odl_res_type.singular: res}

        LOG.debug("Calling sync_from_callback with ODL_OPS (%(odl_ops)s) "
                  "ODL_RES_TYPE (%(odl_res_type)s) RES_ID (%(res_id)s) "
                  "ODL_RES_DICT (%(odl_res_dict)s) KWARGS (%(kwargs)s)",
                  {'odl_ops': odl_ops, 'odl_res_type': odl_res_type,
                   'res_id': res_id, 'odl_res_dict': odl_res_dict,
                   'kwargs': kwargs})

        self.odl_driver.sync_from_callback(odl_ops, odl_res_type,
                                           res_id, odl_res_dict)
