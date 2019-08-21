"""
 ****************************************************************************
 Filename:          realstor_psu_sensor.py
 Description:       Monitors PSU using RealStor API.
 Creation Date:     06/24/2019
 Author:            Malhar Vora

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 ****************************************************************************
"""
import errno
import json
import os
import re

import requests
from zope.interface import implements

from framework.base.module_thread import ScheduledModuleThread
from framework.base.internal_msgQ import InternalMsgQ
from framework.utils.service_logging import logger
from framework.platforms.realstor.realstor_enclosure import singleton_realstorencl

# Modules that receive messages from this module
from message_handlers.real_stor_encl_msg_handler import RealStorEnclMsgHandler

from sensors.Ipsu import IPSUsensor


class RealStorPSUSensor(ScheduledModuleThread, InternalMsgQ):
    """Monitors PSU data using RealStor API"""

    implements(IPSUsensor)

    SENSOR_NAME = "RealStorPSUSensor"
    SENSOR_RESP_TYPE = "enclosure_psu_alert"
    RESOURCE_CATEGORY = "fru"

    PRIORITY = 1

    # PSUs directory name
    PSUS_DIR = "psus"

    @staticmethod
    def name():
        """@return: name of the monitoring module."""
        return RealStorPSUSensor.SENSOR_NAME

    def __init__(self):
        super(RealStorPSUSensor, self).__init__(
            self.SENSOR_NAME, self.PRIORITY)

        self._faulty_psu_file_path = None

        self.rssencl = singleton_realstorencl

        # psus persistent cache
        self.psu_prcache = None

        # Holds PSUs with faults. Used for future reference.
        self._previously_faulty_psus = {}

    def initialize(self, conf_reader, msgQlist, products):
        """initialize configuration reader and internal msg queues"""

        # Initialize ScheduledMonitorThread and InternalMsgQ
        super(RealStorPSUSensor, self).initialize(conf_reader)

        # Initialize internal message queues for this module
        super(RealStorPSUSensor, self).initialize_msgQ(msgQlist)

        self.psu_prcache = os.path.join(self.rssencl.frus, self.PSUS_DIR)

        # Create internal directory structure  if not present
        self.rssencl.check_prcache(self.psu_prcache)

        # Persistence file location. This file stores faulty PSU data
        self._faulty_psu_file_path = os.path.join(
            self.psu_prcache, "psudata.json")
        self._log_debug(
            "_faulty_psu_file_path: {0}".format(self._faulty_psu_file_path))

        # Load faulty PSU data from file if available
        self._previously_faulty_psus = self.rssencl.jsondata.load(\
                                           self._faulty_psu_file_path)

        if self._previously_faulty_psus == None:
            self._previously_faulty_psus = {}
            self.rssencl.jsondata.dump(self._previously_faulty_psus,\
                self._faulty_psu_file_path)

    def read_data(self):
        """This method is part of interface. Currently it is not
        in use.
        """
        return {}

    def run(self):
        """Run the sensor on its own thread"""

        # Check for debug mode being activated
        self._read_my_msgQ_noWait()

        psus = None
        try:
            psus = self._get_psus()

            if psus:
                self._get_msgs_for_faulty_psus(psus)

        except Exception as exception:
            logger.exception(exception)

        # Reset debug mode if persistence is not enabled
        self._disable_debug_if_persist_false()

        # Fire every 10 seconds to see if We have a faulty PSU
        self._scheduler.enter(10, self._priority, self.run, ())

    def _get_psus(self):
        """Receives list of PSUs from API.
           URL: http://<host>/api/show/power-supplies
        """
        url = self.rssencl.build_url(
                  self.rssencl.URI_CLIAPI_SHOWPSUS)

        response = self.rssencl.ws_request(
                        url, self.rssencl.ws.HTTP_GET)

        if not response:
            logger.warn("{0}:: PSUs status unavailable as ws request {1}"
                " failed".format(self.rssencl.EES_ENCL, url))
            return

        if response.status_code != self.rssencl.ws.HTTP_OK:
            logger.error("{0}:: http request {1} to get power-supplies failed "
                " with err {2}" % self.rssencl.EES_ENCL, url,
                response.status_code)
            return

        response_data = json.loads(response.text)
        psus = response_data.get("power-supplies")
        return psus

    def _get_msgs_for_faulty_psus(self, psus, send_message=True):
        """Checks for health of psus and returns list of messages to be
           sent to handler if there are any.
        """
        self._log_debug(
            "RealStorPSUSensor._get_msgs_for_faulty_psus -> {0} {1}".format(
                psus, send_message))
        faulty_psu_messages = []
        internal_json_msg = None
        psu_health = None
        durable_id = None
        alert_type = ""
        # Flag to indicate if there is a change in _previously_faulty_psus
        state_changed = False

        if not psus:
            return

        for psu in psus:
            psu_health = psu["health"].lower()
            durable_id = psu["durable-id"]
            psu_health_reason = psu["health-reason"]
            # Check for missing and fault case
            if psu_health == self.rssencl.HEALTH_FAULT:
                self._log_debug("Found fault in PSU {0}".format(durable_id))
                if durable_id not in self._previously_faulty_psus:
                    alert_type = self.rssencl.FRU_FAULT
                    # Check for removal
                    if self._check_if_psu_not_installed(psu_health_reason):
                        alert_type = self.rssencl.FRU_MISSING
                    self._previously_faulty_psus[durable_id] = {
                        "health": psu_health, "alert_type": alert_type}
                    state_changed = True
                    internal_json_msg = self._create_internal_msg(
                        psu, alert_type)
                    faulty_psu_messages.append(internal_json_msg)
                    # Send message to handler
                    if send_message:
                        self._send_json_msg(internal_json_msg)
            # Check for fault case
            elif psu_health == self.rssencl.HEALTH_DEGRADED:
                self._log_debug("Found degraded in PSU {0}".format(durable_id))
                if durable_id not in self._previously_faulty_psus:
                    alert_type = self.rssencl.FRU_FAULT
                    self._previously_faulty_psus[durable_id] = {
                        "health": psu_health, "alert_type": alert_type}
                    state_changed = True
                    internal_json_msg = self._create_internal_msg(
                        psu, alert_type)
                    faulty_psu_messages.append(internal_json_msg)
                    # Send message to handler
                    if send_message:
                        self._send_json_msg(internal_json_msg)
            # Check for healthy case
            elif psu_health == self.rssencl.HEALTH_OK:
                self._log_debug("Found ok in PSU {0}".format(durable_id))
                if durable_id in self._previously_faulty_psus:
                    # Send message to handler
                    if send_message:
                        previous_alert_type = \
                            self._previously_faulty_psus[durable_id]["alert_type"]
                        alert_type = self.rssencl.FRU_FAULT_RESOLVED
                        if previous_alert_type == self.rssencl.FRU_MISSING:
                            alert_type = self.rssencl.FRU_INSERTION
                        internal_json_msg = self._create_internal_msg(
                            psu, alert_type)
                        faulty_psu_messages.append(internal_json_msg)
                        if send_message:
                            self._send_json_msg(internal_json_msg)
                    del self._previously_faulty_psus[durable_id]
                    state_changed = True
            # Persist faulty PSU list to file only if something is changed
            if state_changed:
                self.rssencl.jsondata.dump(self._previously_faulty_psus,\
                    self._faulty_psu_file_path)
                state_changed = False
            alert_type = ""
        return faulty_psu_messages

    def _create_internal_msg(self, psu_detail, alert_type):
        """Forms a dictionary containing info about PSUs to send to
           message handler.
        """
        self._log_debug(
            "RealStorPSUSensor._create_internal_msg -> {0} {1}".format(
                psu_detail, alert_type))
        if not psu_detail:
            return {}

        info = {
            "enclosure-id": psu_detail.get("enclosure-id"),
            "serial-number":  psu_detail.get("serial-number"),
            "description":  psu_detail.get("description"),
            "revision":  psu_detail.get("revision"),
            "model":  psu_detail.get("model"),
            "vendor":  psu_detail.get("vendor"),
            "location":  psu_detail.get("location"),
            "part-number":  psu_detail.get("part-number"),
            "fru-shortname":  psu_detail.get("fru-shortname"),
            "mfg-date":  psu_detail.get("mfg-date"),
            "mfg-vendor-id":  psu_detail.get("mfg-vendor-id"),
            "dc12v":  psu_detail.get("dc12v"),
            "dc5v":  psu_detail.get("dc12v"),
            "dc33v":  psu_detail.get("dc33v"),
            "dc12i":  psu_detail.get("dc12i"),
            "dc5i":  psu_detail.get("dc5i"),
            "dctemp":  psu_detail.get("dctemp"),
            "health":  psu_detail.get("health"),
            "health-reason":  psu_detail.get("health-reason"),
            "health-recommendation":  psu_detail.get("health-recommendation"),
            "status":  psu_detail.get("status")
        }
        extended_info = {
            "durable-id":  psu_detail.get("durable-id"),
            "position":  psu_detail.get("position"),
        }
        internal_json_msg = json.dumps(
            {"sensor_request_type": {
                "enclosure_alert": {
                    "sensor_type": self.SENSOR_RESP_TYPE,
                    "resource_type": self.RESOURCE_CATEGORY,
                    "alert_type": alert_type,
                    "status": "update"
                },
                "info": info,
                "extended_info": extended_info
            }})
        return internal_json_msg

    def _send_json_msg(self, json_msg):
        """Sends JSON message to Handler"""
        self._log_debug(
            "RealStorPSUSensor._send_json_msg -> {0}".format(json_msg))
        if not json_msg:
            return
        self._write_internal_msgQ(RealStorEnclMsgHandler.name(), json_msg)

    def _check_if_psu_not_installed(self, health_reason):
        """Checks if PSU is not installed by checking <not installed>
            line in health-reason key. It uses re.findall method to
            check if desired string exists in health-reason. Returns
            boolean based on length of the list of substrings found
            in health-reason. So if length is 0, it returns False,
            else True.
        """
        return bool(re.findall("not installed", health_reason))

    def shutdown(self):
        """Clean up scheduler queue and gracefully shutdown thread"""
        super(RealStorPSUSensor, self).shutdown()