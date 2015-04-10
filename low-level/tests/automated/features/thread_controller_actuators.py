# -*- coding: utf-8 -*-
from lettuce import *

import os
import json

# Add the top level directory to the sys.path to access classes
topdir = os.path.dirname(os.path.dirname(os.path.dirname \
            (os.path.dirname(os.path.abspath(__file__)))))
os.sys.path.insert(0, topdir)

from tests.automated.rabbitmq.rabbitmq_ingress_processor_tests import RabbitMQingressProcessorTests
from framework.rabbitmq.rabbitmq_egress_processor import RabbitMQegressProcessor


@step(u'Given I send in the actuator message to restart drive manager')
def given_i_send_in_the_actuator_message_to_restart_drive_manager(step):    
    egressMsg = {
        "title": "SSPL-LL Actuator Request",
        "description": "Seagate Storage Platform Library - Low Level - Actuator Request",

        "sspl_ll_msg_header": {
            "schema_version": "1.0.0",
            "sspl_version": "1.0.0",
            "msg_version": "1.0.0"
        },
        "actuator_request_type": {
            "thread_controller": {
                "module_name" : "DriveManager",
                "thread_request": "restart"
            }
        }
    }
    world.sspl_modules[RabbitMQegressProcessor.name()]._write_internal_msgQ(RabbitMQegressProcessor.name(), egressMsg)

@step(u"When SSPL-LL restarts the thread for drive manager msg handler")
def when_SSPL_LL_restarts_the_thread(step):
    print("SSPL-LL restarts the threads for drive manager msg handler")
    # TODO: Use an instance of JournalD sensor to monitor logs showing that SSPL-LL performed the correct action

@step(u"Then I get the Restart Successful JSON response message")
def then_i_receive_Restart_Successful_JSON_response_message(step):
    """I get the JSON response msg with 'thread_response': 'Restart Successful' key value"""
    ingressMsg = world.sspl_modules[RabbitMQingressProcessorTests.name()]._read_my_msgQ()
    print("Received: %s" % ingressMsg)
    
    # Verify module name and thread response
    module_name = ingressMsg.get("actuator_response_type").get("thread_controller").get("module_name")
    print("module_name: %s" % module_name)
    assert module_name == "DriveManager"
    
    thread_response = ingressMsg.get("actuator_response_type").get("thread_controller").get("thread_response")
    print("thread_response: %s" % thread_response)
    assert thread_response == "Restart Successful"
    print"Done"
    
@step(u'Given I send in the actuator message to stop drive manager')
def given_i_send_in_the_actuator_message_to_stop_drive_manager(step):
    egressMsg = {
        "title": "SSPL-LL Actuator Request",
        "description": "Seagate Storage Platform Library - Low Level - Actuator Request",

        "sspl_ll_msg_header": {
            "schema_version": "1.0.0",
            "sspl_version": "1.0.0",
            "msg_version": "1.0.0"
        },
        "actuator_request_type": {
            "thread_controller": {
                "module_name" : "DriveManager",
                "thread_request": "stop"
            }
        }
    }
    world.sspl_modules[RabbitMQegressProcessor.name()]._write_internal_msgQ(RabbitMQegressProcessor.name(), egressMsg)

@step(u'When SSPL-LL Stops the thread for drive manager msg handler')
def when_sspl_ll_stops_the_thread_for_drive_manager_msg_handler(step):
    print("SSPL-LL Stops the thread for drive manager msg handler")
    # TODO: Use an instance of JournalD sensor to monitor logs showing that SSPL-LL performed the correct action

@step(u'Then I get the Stop Successful JSON response message')
def then_i_get_the_stop_successful_json_response_message(step):
    """I get the JSON response msg with 'thread_response': 'Stop Successful' key value"""
    ingressMsg = world.sspl_modules[RabbitMQingressProcessorTests.name()]._read_my_msgQ()
    print("Received: %s" % ingressMsg)
    
    # Verify module name and thread response
    module_name = ingressMsg.get("actuator_response_type").get("thread_controller").get("module_name")
    print("module_name: %s" % module_name)
    assert module_name == "DriveManager"
    
    thread_response = ingressMsg.get("actuator_response_type").get("thread_controller").get("thread_response")
    print("thread_response: %s" % thread_response)
    assert thread_response == "Stop Successful"
    print"Done"

@step(u'Given I send in the actuator message to start drive manager')
def given_i_send_in_the_actuator_message_to_start_drive_manager(step):
    egressMsg = {
        "title": "SSPL-LL Actuator Request",
        "description": "Seagate Storage Platform Library - Low Level - Actuator Request",

        "sspl_ll_msg_header": {
            "schema_version": "1.0.0",
            "sspl_version": "1.0.0",
            "msg_version": "1.0.0"
        },
        "actuator_request_type": {
            "thread_controller": {
                "module_name" : "DriveManager",
                "thread_request": "start"
            }
        }
    }
    world.sspl_modules[RabbitMQegressProcessor.name()]._write_internal_msgQ(RabbitMQegressProcessor.name(), egressMsg)

@step(u'When SSPL-LL Starts the thread for drive manager msg handler')
def when_sspl_ll_starts_the_thread_for_drive_manager_msg_handler(step):
    print("SSPL-LL Starts the thread for drive manager msg handler")
    # TODO: Use an instance of JournalD sensor to monitor logs showing that SSPL-LL performed the correct action

@step(u'Then I get the Start Successful JSON response message')
def then_i_get_the_start_successful_json_response_message(step):
    """I get the JSON response msg with 'thread_response': 'Stop Successful' key value"""
    ingressMsg = world.sspl_modules[RabbitMQingressProcessorTests.name()]._read_my_msgQ()
    print("Received: %s" % ingressMsg)

    # Verify module name and thread response
    module_name = ingressMsg.get("actuator_response_type").get("thread_controller").get("module_name")
    print("module_name: %s" % module_name)
    assert module_name == "DriveManager"

    thread_response = ingressMsg.get("actuator_response_type").get("thread_controller").get("thread_response")
    print("thread_response: %s" % thread_response)
    assert thread_response == "Start Successful"
    print"Done"

@step(u'Given I request to stop drive manager and then I request a thread status')
def given_i_request_to_stop_drive_manager_and_then_i_request_a_thread_status(step):
    egressMsg = {
        "title": "SSPL-LL Actuator Request",
        "description": "Seagate Storage Platform Library - Low Level - Actuator Request",

        "sspl_ll_msg_header": {
            "schema_version": "1.0.0",
            "sspl_version": "1.0.0",
            "msg_version": "1.0.0"
        },
        "actuator_request_type": {
            "thread_controller": {
                "module_name" : "DriveManager",
                "thread_request": "stop"
            }
        }
    }
    world.sspl_modules[RabbitMQegressProcessor.name()]._write_internal_msgQ(RabbitMQegressProcessor.name(), egressMsg)

    # Request the status for the stopped thread
    egressMsg = {
        "title": "SSPL-LL Actuator Request",
        "description": "Seagate Storage Platform Library - Low Level - Actuator Request",

        "sspl_ll_msg_header": {
            "schema_version": "1.0.0",
            "sspl_version": "1.0.0",
            "msg_version": "1.0.0"
        },
        "actuator_request_type": {
            "thread_controller": {
                "module_name" : "DriveManager",
                "thread_request": "status"
            }
        }
    }
    world.sspl_modules[RabbitMQegressProcessor.name()]._write_internal_msgQ(RabbitMQegressProcessor.name(), egressMsg)

@step(u'When SSPL-LL Stops the drive manager and receives a request for thread status')
def when_sspl_ll_stops_the_drive_manager_and_receives_a_request_for_thread_status(step):
    print("SSPL-LL Starts the thread for drive manager msg handler")
    # TODO: Use an instance of JournalD sensor to monitor logs showing that SSPL-LL performed the correct action

@step(u'Then I get the Stop Successful JSON message then I get the thread status message')
def then_i_get_the_stop_successful_json_message_then_i_get_the_thread_status_message(step):
    """I get the JSON response msg with 'thread_response': 'Stop Successful' key value"""
    ingressMsg = world.sspl_modules[RabbitMQingressProcessorTests.name()]._read_my_msgQ()
    print("Received: %s" % ingressMsg)

    # Verify module name and thread response
    module_name = ingressMsg.get("actuator_response_type").get("thread_controller").get("module_name")
    print("module_name: %s" % module_name)
    assert module_name == "DriveManager"

    thread_response = ingressMsg.get("actuator_response_type").get("thread_controller").get("thread_response")
    print("thread_response: %s" % thread_response)
    assert thread_response == "Stop Successful"

    ingressMsg = world.sspl_modules[RabbitMQingressProcessorTests.name()]._read_my_msgQ()
    print("Received: %s" % ingressMsg)

    # Verify module name and thread response
    module_name = ingressMsg.get("actuator_response_type").get("thread_controller").get("module_name")
    print("module_name: %s" % module_name)
    assert module_name == "DriveManager"
    
    thread_response = ingressMsg.get("actuator_response_type").get("thread_controller").get("thread_response")
    print("thread_response: %s" % thread_response)
    assert thread_response == "Status: Halted"
    print"Done"

@step(u'Given I request to start drive manager and then I request a thread status')
def given_i_request_to_start_drive_manager_and_then_i_request_a_thread_status(step):
    egressMsg = {
        "title": "SSPL-LL Actuator Request",
        "description": "Seagate Storage Platform Library - Low Level - Actuator Request",

        "sspl_ll_msg_header": {
             "schema_version": "1.0.0",
             "sspl_version": "1.0.0",
             "msg_version": "1.0.0"
        },
        "actuator_request_type": {
            "thread_controller": {
                 "module_name" : "DriveManager",
                 "thread_request": "start"
            }
        }
    }
    world.sspl_modules[RabbitMQegressProcessor.name()]._write_internal_msgQ(RabbitMQegressProcessor.name(), egressMsg)

    # Request the status for the stopped thread
    egressMsg = {
        "title": "SSPL-LL Actuator Request",
        "description": "Seagate Storage Platform Library - Low Level - Actuator Request",

        "sspl_ll_msg_header": {
            "schema_version": "1.0.0",
            "sspl_version": "1.0.0",
            "msg_version": "1.0.0"
        },
        "actuator_request_type": {
            "thread_controller": {
                "module_name" : "DriveManager",
                "thread_request": "status"
            }
        }
    }
    world.sspl_modules[RabbitMQegressProcessor.name()]._write_internal_msgQ(RabbitMQegressProcessor.name(), egressMsg)

@step(u'When SSPL-LL Starts the drive manager and receives a request for thread status')
def when_sspl_ll_starts_the_drive_manager_and_receives_a_request_for_thread_status(step):
    print("SSPL-LL Starts the thread for drive manager msg handler")
    # TODO: Use an instance of JournalD sensor to monitor logs showing that SSPL-LL performed the correct action

@step(u'Then I get the Start Successful JSON message then I get the thread status message')
def then_i_get_the_start_successful_json_message_then_i_get_the_thread_status_message(step):
    """I get the JSON response msg with 'thread_response': 'Stop Successful' key value"""
    ingressMsg = world.sspl_modules[RabbitMQingressProcessorTests.name()]._read_my_msgQ()
    print("Received: %s" % ingressMsg)

    # Verify module name and thread response
    module_name = ingressMsg.get("actuator_response_type").get("thread_controller").get("module_name")
    print("module_name: %s" % module_name)
    assert module_name == "DriveManager"

    thread_response = ingressMsg.get("actuator_response_type").get("thread_controller").get("thread_response")
    print("thread_response: %s" % thread_response)
    assert thread_response == "Start Successful"

    ingressMsg = world.sspl_modules[RabbitMQingressProcessorTests.name()]._read_my_msgQ()
    print("Received: %s" % ingressMsg)

    # Verify module name and thread response
    module_name = ingressMsg.get("actuator_response_type").get("thread_controller").get("module_name")
    print("module_name: %s" % module_name)
    assert module_name == "DriveManager"
    
    thread_response = ingressMsg.get("actuator_response_type").get("thread_controller").get("thread_response")
    print("thread_response: %s" % thread_response)
    assert thread_response == "Status: Running"
    print"Done"






    