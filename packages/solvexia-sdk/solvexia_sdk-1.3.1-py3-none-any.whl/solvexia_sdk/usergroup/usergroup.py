import requests
from solvexia_sdk import api

class userGroup:
    def __init__(self, usergroup_id):
        self.usergroup_id = usergroup_id
    
    def get_usergroup_list(self):
        response = api.api_get("usergroups")
        api.status_code_check(response, "Error getting user group list")
        return response.json()
    
    def get_usergroup(self):
        response = api.api_get(f"usergroups/{self.usergroup_id}")
        api.status_code_check(response, f"Error getting user group with usergroup_id {self.usergroup_id}")
        return response.json()
    
    def get_users(self):
        response = api.api_get(f"usergroups/{self.usergroup_id}/users")
        api.status_code_check(response, f"Error getting user for a user group with usergroup_id {self.usergroup_id}")
        return response.json()

    def add_user(self, user_id):
        payload = {
            "id": user_id
        }
        response = api.api_post(f"usergroups/{self.usergroup_id}/users", payload)
        api.status_code_check(response, f"Error adding user {user_id} to a user group with usergroup_id {self.usergroup_id}")
        return response.json()

    def remove_user(self, user_id):
        response = api.api_delete(f"usergroups/{self.usergroup_id}/users/{user_id}")
        api.status_code_check(response, f"Error removing user {user_id} from a user group with usergroup_id {self.usergroup_id}")

    def get_permissions(self):
        response = api.api_get(f"usergroups/{self.usergroup_id}/permissions")
        api.status_code_check(response, f"Error getting user group permissions with usergroup_id {self.usergroup_id}")
        return response.json()

    def add_permission(self, resource_id, role):
        payload = {
            'resourceId': resource_id,
            'role': role
        }
        response = api.api_post(f"usergroups/{self.usergroup_id}/permissions", payload)
        api.status_code_check(response, f"Error adding user group permissions with usergroup_id {self.usergroup_id} for resource_id {resource_id}")
        return response.json()

    def update_permission(self, resource_id, role):
        payload = {
            'role': role
        }
        response = api.api_post(f"usergroups/{self.usergroup_id}/permissions/{resource_id}", payload)
        api.status_code_check(response, f"Error updating user group permissions with usergroup_id {self.usergroup_id} for resource_id {resource_id}")
        return response.json()
    
    def delete_permission(self, resource_id):
        response = api.api_delete(f"usergroups/{self.usergroup_id}/permissions/{resource_id}")
        api.status_code_check(response, f"Error deleting user group permissions with usergroup_id {self.usergroup_id} for resource_id {resource_id}")
