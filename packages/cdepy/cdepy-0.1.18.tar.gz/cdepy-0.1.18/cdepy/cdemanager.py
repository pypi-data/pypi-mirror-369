"""
Module to manage CDE Clusters
"""

from cdepy.cdeconnection import CdeConnection
import requests
from datetime import datetime
import pytz
import numpy as np
import pandas as pd
from os.path import exists
from requests_toolbelt import MultipartEncoder
import xmltodict as xd
import pyparsing
import os, json, requests, re, sys


class CdeClusterManager:
    """
    Class to manage CDE Clusters
    """

    def __init__(self, cdeConnection):
        self.clusterConnection = cdeConnection
        self.JOBS_API_URL = self.clusterConnection.JOBS_API_URL
        self.TOKEN = self.clusterConnection.TOKEN


    def createJob(self, cdeJobDefinition):
        """
        Method to create a CDE Job
        Requires cdeJobDefinition of type cdeAirflowJobDefinition or cdeSparkJobDefinition as input for payload
        """

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        PUT = '{}/jobs'.format(self.JOBS_API_URL)

        data = json.dumps(cdeJobDefinition)

        x = requests.post(PUT, headers=headers, data=data)

        if x.status_code == 201:
            print("CDE Job Creation Succeeded\n")
        else:
            print(x.status_code)
            print(x.text)


    def deleteJob(self, cdeJobName):
        """
        Method to delete job
        Requires cdeJobName as shown in the CDE Jobs UI
        """

        url = self.JOBS_API_URL + "/jobs/" + cdeJobName

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        x = requests.delete(url, headers=headers)

        if x.status_code == 201:
            print("CDE Job Creation Succeeded\n")
        else:
            print(x.status_code)
            print(x.text)


    def updateJob(self, cdeJobName, cdeJobDefinition):
        """
        Method to update job definition
        Requires cdeJobName as shown in the CDE Jobs UI
        Requires cdeJobDefinition of type cdeAirflowJobDefinition or cdeSparkJobDefinition as input for payload
        """

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        PUT = '{}/jobs'.format(self.JOBS_API_URL)

        data = json.dumps(cdeJobDefinition)

        x = requests.post(PUT, headers=headers, data=data)

        if x.status_code == 201:
            print("CDE Job Update Succeeded\n")
        else:
            print(x.status_code)
            print(x.text)


    def showAvailableLogTypes(self, jobRunId):
        """
        Method to show all available log types for a specific Job Run
        Job Log Types for Spark Jobs are:
        1) driver/stdout
        2) driver/stderr
        3) driver/k8sevents i.e. Pod Event Logs
        4) driver/event i.e. Spark Event Logs
        5) executor_n/stdout e.g. executor_1/stdout, executor_2/stdout
        6) driver/tgtloader
        7) driver/workspace-init
        8) submitter/stderr
        9) submitter/stdout
        10) submitter/k8s
        11) submitter/jobs_api
        """

        url = self.JOBS_API_URL + "/job-runs/" + jobRunId + "/log-types"

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        x = requests.get(url, headers=headers)

        return x.text

        if x.status_code == 201:
            print("Downloading Job Logs Succeeded")
        else:
            print(x.status_code)
            print(x.text)


    def downloadJobRunLogs(self, jobRunId, logsType):
        """
        Method to download all logs for specified jobrun
        Requires jobRunId; jobRunId is an integer; jobRunId can be obtained by running listJobRuns
        """

        url = self.JOBS_API_URL + "/job-runs/" + jobRunId + "/logs?type=" + logsType

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        x = requests.get(url, headers=headers)

        return x.text

        if x.status_code == 201:
            print("Downloading Job Logs Succeeded")
        else:
            print(x.status_code)
            print(x.text)


    def listJobs(self):
        """
        Method to list CDE Jobs as shown in the CDE Jobs UI
        Shows all jobs in the CDE Virtual Cluster
        """

        url = self.JOBS_API_URL + "/jobs"

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        x = requests.get(url+'?latestjob=false&limit=100&offset=0&orderby=name&orderasc=true', headers=headers)

        return x.text

        if x.status_code == 201:
            print("Listing Jobs Succeeded")
        else:
            print(x.status_code)
            print(x.text)


    def listJobRuns(self, type=None):
        """
        Method to show all CDE Jobs that have been executed in the cluster
        Does not require input
        """

        tz_LA = pytz.timezone('America/Los_Angeles')
        now = datetime.now(tz_LA)
        print("Listing Jobs as of: {} PACIFIC STANDARD TIME\n".format(now))


        url = self.JOBS_API_URL + "/job-runs"

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if type=="spark":
            x = requests.get(url+'?filter=type%5Beq%5Dspark&limit=100&offset=0&orderby=ID&orderasc=false', headers=headers)
        elif type=="airflow":
            x = requests.get(url+'?filter=type%5Beq%5Dairflow&limit=100&offset=0&orderby=ID&orderasc=false', headers=headers)
        else:
            x = requests.get(url+'?limit=100&offset=0&orderby=ID&orderasc=false', headers=headers)

        return x.text

        if x.status_code == 201:
            print("Listing Jobs Succeeded")
        else:
            print(x.status_code)
            print(x.text)


    def runJob(self, CDE_JOB_NAME, SPARK_OVERRIDES=None, AIRFLOW_OVERRIDES=None):
        """
        Method to trigger execution of CDE Job
        CDE Job could be of type Spark or Airflow
        The method assumes the CDE Job has already been created in the CDE Virtual Cluster
        """
        overrides = {}

        if SPARK_OVERRIDES != None and AIRFLOW_OVERRIDES != None:
            print("Error: Spark Overrides and Airflow Overrides Specified\n")
            print("You can only specify either Spark Overrides or Airflow Overrides, but not both!")
        elif SPARK_OVERRIDES != None and AIRFLOW_OVERRIDES == None and isinstance(SPARK_OVERRIDES, dict):
            overrides = {"overrides": SPARK_OVERRIDES}
        elif AIRFLOW_OVERRIDES != None and SPARK_OVERRIDES == None and isinstance(AIRFLOW_OVERRIDES, dict):
            overrides = {"overrides": AIRFLOW_OVERRIDES}

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        POST = "{}/jobs/".format(self.JOBS_API_URL)+CDE_JOB_NAME+"/run"

        data = json.dumps(overrides)

        x = requests.post(POST, headers=headers, data=data)

        if x.status_code == 201:
            print("CDE Job Submission has Succeeded\n")
            print("Please visit the CDE Job Runs UI to validate CDE Job Status\n")
        else:
            print(x.status_code)
            print(x.text)


    def createResource(self, cdeRsourceDefinition):
        """
        Method to create CDE Resource
        Requires cdeRsourceDefinition as input
        Accepts types Files or Python
        e.g. cdeRsourceDefinition = {"name": str(resource_name)}
        """

        print("CDE Resource Creation in Progress\n")

        url = self.JOBS_API_URL + "/resources"
        data_to_send = json.dumps(cdeRsourceDefinition).encode("utf-8")

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        x = requests.post(url, data=data_to_send, headers=headers)

        if x.status_code == 201:
            print("CDE Resource Created Successfully")
        else:
            print(x.status_code)
            print(x.text)


    def deleteResource(self, cdeResourceName):
        """
        Method to delete CDE Resource
        Requires cdeRsourceDefinition name as input
        e.g. cdeResourceName = str(resource_name)
        """

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        url = self.JOBS_API_URL + "/resources/" + cdeResourceName

        x = requests.delete(url, headers=headers)

        if x.status_code == 204:
            print("CDE Resource {} Deleted Successfully\n".format(cdeResourceName))
        else:
            print(x.status_code)
            print(x.text)


    def describeResource(self, CDE_RESOURCE_NAME, includeFiles = True):
        """
        Method to get resource configuration and content
        """

        if includeFiles == True:
            url = self.JOBS_API_URL + "/resources/" + CDE_RESOURCE_NAME + "?includeFiles=true"
        elif includeFiles == False:
            url = self.JOBS_API_URL + "/resources/" + CDE_RESOURCE_NAME + "?includeFiles=false"
        else:
            print("Error: Include Files Flag can only be set to True or False")

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        x = requests.get(url, headers=headers)

        return x.text

        if x.status_code == 201:
            print("Downloading Job Logs Succeeded")
        else:
            print(x.status_code)
            print(x.text)


    #Upload Spark CDE Job file to CDE Resource
    def uploadFileToResource(self, CDE_RESOURCE_NAME, LOCAL_FILE_PATH, LOCAL_FILE_NAME):
        """
        Method to uplaod files from local to CDE Resource
        Can be used to:
            1) upload files to a CDE Resource of type Files
            2) uplaod a "requirements.txt" file to a CDE Resource of type Python Environment
        Requires a CDE_RESOURCE_NAME, LOCAL_FILE_PATH and LOCAL_FILE_NAME
        e.g. "myCdeFilesResource", "~/myfiles/cdefiles", and "mySparkScript.py"
        e.g. "myCdePythonResource", "~/myfiles/cdefiles", and "requirements.txt"
        """

        print("Uploading File {0} to CDE Resource {1}\n".format(LOCAL_FILE_NAME, CDE_RESOURCE_NAME))

        m = MultipartEncoder(
            fields={
                    'file': ('filename', open(LOCAL_FILE_PATH+"/"+LOCAL_FILE_NAME, 'rb'), 'text/plain')}
            )

        PUT = '{jobs_api_url}/resources/{resource_name}/{file_name}'.format(jobs_api_url=self.JOBS_API_URL, resource_name=CDE_RESOURCE_NAME, file_name=LOCAL_FILE_NAME)

        x = requests.put(PUT, data=m, headers={'Authorization': f"Bearer {self.TOKEN}",'Content-Type': m.content_type})
        print("Response Status Code {}".format(x.status_code))

        if x.status_code == 201:
            print("Uploading File {0} to CDE Resource {1} has Succeeded\n".format(LOCAL_FILE_NAME, CDE_RESOURCE_NAME))
        else:
            print(x.status_code)
            print(x.text)


    def uploadArchiveToResource(self, CDE_RESOURCE_NAME, LOCAL_FILE_PATH, LOCAL_FILE_NAME):
        """
        Method to Upload an archive(.zip or .tar.gz archives)
        to the resource with an optional directory prefix.
        New files are added and existing files are overwritten
        """

        raise NotImplementedError


    def removeFileFromResource(self, CDE_RESOURCE_NAME, RESOURCE_FILE_NAME):
        """
        Method to remove a file from a CDE Resource of type Files
        """

        url = self.JOBS_API_URL + "/resources/" + CDE_RESOURCE_NAME + "/" + RESOURCE_FILE_NAME

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        x = requests.delete(url, headers=headers)

        if x.status_code == 201:
            print("File Removal Succeeded\n")
        else:
            print(x.status_code)
            print(x.text)


    def downloadFileFromResource(self, CDE_RESOURCE_NAME, RESOURCE_FILE_NAME):
        """
        Method to download a file in the resource at the path specified
        """

        url = self.JOBS_API_URL + "/resources/" + CDE_RESOURCE_NAME + "/" + RESOURCE_FILE_NAME

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/octet-stream',
            'Content-Type': 'application/json',
        }

        x = requests.get(url, headers=headers)

        return x.text

        if x.status_code == 201:
            print("Downloading Resource File Succeeded")
        else:
            print(x.status_code)
            print(x.text)


    def pauseAllJobs(self):
        """
        Method to pause all jobs in a CDE Virtual Cluster
        """
        raise NotImplementedError


    def unpauseAllJobs(self):
        """
        Method to unpuase all paused jobs in a CDE Virtual Cluster
        """
        raise NotImplementedError


    def pauseSingleJob(self, CDE_JOB_NAME):
        """
        Method to pause a single unpaused job
        """

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        POST = "{}/jobs/".format(self.JOBS_API_URL) + CDE_JOB_NAME + "/schedule/pause"

        x = requests.post(POST, headers=headers)

        if x.status_code == 201:
            print("CDE Job Submission has Succeeded\n")
            print("Please visit the CDE Job Runs UI to validate CDE Job Status\n")
        else:
            print(x.status_code)
            print(x.text)


    def unpauseSingleJob(self, CDE_JOB_NAME):
        """
        Method to unpuase a single paused job
        """

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        POST = "{}/jobs/".format(self.JOBS_API_URL) + CDE_JOB_NAME + "/schedule/unpause"

        x = requests.post(POST, headers=headers)

        if x.status_code == 201:
            print("CDE Job Submission has Succeeded\n")
            print("Please visit the CDE Job Runs UI to validate CDE Job Status\n")
        else:
            print(x.status_code)
            print(x.text)


    def listVcMeta(self):
        """
        Method to provide configuration information
        and useful parameters for the CDE Virtual Cluster
        """

        headers = {
            'Authorization': f"Bearer {self.TOKEN}",
            'accept': 'application/json',
            'Content-Type': 'application/json',
            }

        x = requests.get(self.JOBS_API_URL+'/info', headers=headers)

        return json.loads(x.text)
