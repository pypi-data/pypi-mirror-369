import requests
import json
import sys
from solvexia_sdk import api
from solvexia_sdk.datasteps import datasteps

class processRuns:
    def __init__(self, process_run_id):
        self.process_run_id = process_run_id

    def get_process_run(self):
        response = api.api_get(f"processruns/{self.process_run_id}")
        api.status_code_check(response, f"Error getting the specified process run with process_run_id {self.process_run_id}")
        return response.json()
    
    def start_process_run(self):
        response = api.api_post_no_payload(f"processruns/{self.process_run_id}/start")
        api.status_code_check(response, f"Error starting process run with process_run_id {self.process_run_id}")
        return response.json()

    def cancel_process_run(self):
        response = api.api_post_no_payload(f"processruns/{self.process_run_id}/cancel")
        api.status_code_check(response, f"Error cancelling process run with process_run_id {self.process_run_id}")
        return response.json()

    def restart_process_run_from_step(self, step_id):
        response = api.api_post_no_payload(f"processruns/{self.process_run_id}/steps/{step_id}/restartfromhere")
        api.status_code_check(response, f"Error restarting process run with process_run_id {self.process_run_id} from step with step_id {step_id}")
        return response.json()    

    def get_process_run_status(self):
        response = api.api_get(f"processruns/{self.process_run_id}/runstatus")
        api.status_code_check(response, f"Error getting run status of a process run with process_run_id {self.process_run_id}")
        return response.json()

    def get_process_run_data_steps_list(self):
        response = api.api_get(f"processruns/{self.process_run_id}/steps")
        api.status_code_check(response, f"Error getting list of data steps of process run with process_run_id {self.process_run_id}")
        return response.json()

    def get_process_run_step_runstatus(self, step_id):
        response = api.api_get(f"processruns/{self.process_run_id}/steps/{step_id}/runstatus")
        api.status_code_check(response, f"Error getting run status for step with step_id {step_id} of a process run with process_run_id {self.process_run_id}")
        return response.json()

    def get_process_run_file_list(self):
        processRunFileList = []
        response = self.get_process_run_data_steps_list()
        for x in response:
            individualDS = datasteps.dataSteps(x["id"])
            dsList = individualDS.get_data_step_file_list()
            for y in dsList:
                processRunFileList.append(y)

        return processRunFileList
