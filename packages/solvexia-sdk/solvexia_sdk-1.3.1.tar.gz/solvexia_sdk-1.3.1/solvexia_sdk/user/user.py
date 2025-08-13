import requests
from solvexia_sdk import api

class user:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def get_user_list(self):
        response = api.api_get("users")
        api.status_code_check(response, "Error getting user list")
        return response.json()
    
    def get_user(self):
        response = api.api_get(f"users/{self.user_id}")
        api.status_code_check(response, f"Error getting user with user_id {self.user_id}")
        return response.json()

    def get_groups_user_belong_to(self):
        response = api.api_get(f"users/{self.user_id}/usergroups")
        api.status_code_check(response, f"Error getting user group that a user belong to with user_id {self.user_id}")
        return response.json()

    def create_user(self, email, firstName, lastName, password, userRole, timezone):
        payload = {
            'email': email,
            "firstName": firstName,
            "lastName": lastName,
            "password": password,
            "userRole": userRole,
            "timezone": timezone
        }
        response = api.api_post(f"users", payload)
        api.status_code_check(response, "Error creating user")
        return response.json()

    def update_user(self, firstName, lastName, email, accountStatus, city, country, dateOfBirth, department, phoneNumberLand, phoneNumberMobile, timezone, userRole):
        payload = {}
        if firstName is not None:
            payload["firstName"] = firstName
        if lastName is not None:
            payload["lastName"] = lastName
        if email is not None:
            payload["email"] = email
        if accountStatus is not None:
            payload["accountStatus"] = accountStatus
        if city is not None:
            payload["city"] = city
        if country is not None:
            payload["country"] = country
        if dateOfBirth is not None:
            payload["dateOfBirth"] = dateOfBirth
        if department is not None:
            payload["department"] = department
        if phoneNumberLand is not None:
            payload["phoneNumberLand"] = phoneNumberLand
        if phoneNumberMobile is not None:
            payload["phoneNumberMobile"] = phoneNumberMobile
        if timezone is not None:
            payload["timezone"] = timezone
        if userRole is not None:
            payload["userRole"] = userRole
        response = api.api_post(f"users/{self.user_id}", payload)
        api.status_code_check(response, f"Error updating user with user_id {self.user_id}")
        return response.json()

    def get_permissions(self):
        response = api.api_get(f"users/{self.user_id}/permissions")
        api.status_code_check(response, f"Error getting user's permissions with user_id {self.user_id}")
        return response.json()

    def add_permission(self, resource_id, role):
        payload = {
            'resourceId': resource_id,
            'role': role
        }
        response = api.api_post(f"users/{self.user_id}/permissions", payload)
        api.status_code_check(response, f"Error adding user's permissions with user_id {self.user_id} for resource_id {resource_id}")
        return response.json()

    def update_permission(self, resource_id, role):
        payload = {
            'role': role
        }
        response = api.api_post(f"users/{self.user_id}/permissions/{resource_id}", payload)
        api.status_code_check(response, f"Error updating user's permissions with user_id {self.user_id} for resource_id {resource_id}")
        return response.json()
    
    def delete_permission(self, resource_id):
        response = api.api_delete(f"users/{self.user_id}/permissions/{resource_id}")
        api.status_code_check(response, f"Error deleting user's permissions with user_id {self.user_id} for resource_id {resource_id}")
