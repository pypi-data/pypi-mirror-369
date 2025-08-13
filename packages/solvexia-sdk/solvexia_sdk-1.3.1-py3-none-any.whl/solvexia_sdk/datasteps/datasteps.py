#!/usr/bin/env python

import requests
import json
import sys
from solvexia_sdk import api

class dataSteps:
    def __init__(self, step_id):
        self.step_id = step_id

    def get_data_step(self):
        response = api.api_get(f"steps/{self.step_id}")
        api.status_code_check(response, f"Error getting data step with step_id {self.step_id}")
        return response.json()

    def get_data_step_property_list(self):
        response = api.api_get(f"steps/{self.step_id}/properties")
        api.status_code_check(response, f"Error getting data step property list with step_id {self.step_id}")
        return response.json()

    def get_data_step_property_for_data_step(self, property_id):
        response = api.api_get(f"steps/{self.step_id}/properties/{property_id}")
        api.status_code_check(response, f"Error getting data step property for a data step with step_id {self.step_id} and property_id {property_id}")
        return response.json()

    def update_data_step_property(self, property_id, data_step_instance):
        response = api.api_post(f"steps/{self.step_id}/properties/{property_id}", data_step_instance)
        api.status_code_check(response, f"Error updating data step property with step_id {self.step_id} and property_id {property_id}")
        return response.json()

    def get_data_step_file_list(self):
        final_file_list = []
        datastep_property_list = self.get_data_step_property_list()
        for datastep_property in datastep_property_list:
            if datastep_property["dataType"] == "File":
                final_file_list.append(datastep_property["file"])
        return final_file_list