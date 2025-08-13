import requests
import json
import sys
from solvexia_sdk import api

class table:
    def __init__(self, table_id):
        self.table_id = table_id

    def get_table(self):
        response = api.api_get(f"tables/{self.table_id}")
        api.status_code_check(response, f"Error getting table with table_id {self.table_id}")
        return response.json()

    def create_table(self, name, description):
        payload = {
            'name': name,
            'description': description
        }
        response = api.api_post("tables", payload)
        api.status_code_check(response, f"Error creating table with table_id {self.table_id}")
        return response.json()

    def update_table(self, name, description):
        payload = {
            'name': name,
            'description': description
        }
        response = api.api_post(f"tables/{self.table_id}", payload)
        api.status_code_check(response, f"Error updating table with table_id {self.table_id}")
        return response.json()

    def get_table_columns_list(self):
        response = api.api_get(f"tables/{self.table_id}/columns")
        api.status_code_check(response, f"Error getting table columns with table_id {self.table_id}")
        return response.json()

    def create_column(self, column_instance):
        response = api.api_post(f"tables/{self.table_id}/columns", column_instance)
        api.status_code_check(response, f"Error creating column for table with table_id {self.table_id}")
        return response.json()

    def update_column(self, column_instance, column_name):
        response = api.api_post(f"tables/{self.table_id}/columns/{column_name}", column_instance)
        api.status_code_check(response, f"Error updating column with column_name {column_name} for table with table_id {self.table_id}")
        return response.json()

    def delete_column(self, column_name):
        delete_column_url = api.base_url + f"tables/{self.table_id}/columns/{column_name}"
        response = requests.delete(delete_column_url, headers=api.access_token)
        api.status_code_check(response, f"Error deleting column with column_name {column_name} for table with table_id {self.table_id}")