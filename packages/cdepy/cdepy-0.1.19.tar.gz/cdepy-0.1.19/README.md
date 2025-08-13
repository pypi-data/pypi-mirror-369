# cdepy Package

cdepy is a package for interacting with ***Cludera Data Engineering Virtual Clusters***.

You can find out more about Cloudera Data Engineering in the [Cloudera Documentation](https://docs.cloudera.com/data-engineering/cloud/index.html).

## Usage

You can install this package using

```
pip install cdepy
```

## Features

- CDE Resources: create resources of type Files and Python-Environment
- CDE Jobs: create jobs of type Airflow and Spark
- Job Observability: monitor job status

## Examples

### BASICS

```
from cdepy import cdeconnection
from cdepy import cdejob
from cdepy import cdemanager
from cdepy import cderesource
from cdepy import utils
```

#### Establish Connection to CDE Virtual Cluster

```
JOBS_API_URL = "https://<YOUR-CLUSTER>.cloudera.site/dex/api/v1"
WORKLOAD_USER = "<Your-CDP-Workload-User>"
WORKLOAD_PASSWORD = "<Your-CDP-Workload-Password>"

myCdeConnection = cdeconnection.CdeConnection(JOBS_API_URL, WORKLOAD_USER, WORKLOAD_PASSWORD)

myCdeConnection.setToken()
```

#### Create CDE Files Resource Definition

```
CDE_RESOURCE_NAME = "myFilesCdeResource"
myCdeFilesResource = cderesource.CdeFilesResource(CDE_RESOURCE_NAME)
myCdeFilesResourceDefinition = myCdeFilesResource.createResourceDefinition()
```

#### Create a CDE Spark Job Definition

```
CDE_JOB_NAME = "myCdeSparkJob"
APPLICATION_FILE_NAME = "pysparksql.py"

myCdeSparkJob = cdejob.CdeSparkJob(myCdeConnection)
myCdeSparkJobDefinition = myCdeSparkJob.createJobDefinition(CDE_JOB_NAME, CDE_RESOURCE_NAME, APPLICATION_FILE_NAME, executorMemory="2g", executorCores=2)
```

#### Create Resource and Job in CDE Cluster

```
LOCAL_FILE_PATH = "examples"
LOCAL_FILE_NAME = "pysparksql.py"

myCdeClusterManager = cdemanager.CdeClusterManager(myCdeConnection)


myCdeClusterManager.createResource(myCdeFilesResourceDefinition)
myCdeClusterManager.uploadFileToResource(CDE_RESOURCE_NAME, LOCAL_FILE_PATH, LOCAL_FILE_NAME)

myCdeClusterManager.createJob(myCdeSparkJobDefinition)
```

#### Run Job with Default Configurations

```
myCdeClusterManager.runJob(CDE_JOB_NAME)
```

#### Update Runtime Configurations

```
overrideParams = {"spark": {"executorMemory": "4g"}}
myCdeClusterManager.runJob(CDE_JOB_NAME, SPARK_OVERRIDES=overrideParams)
```

#### Validate Job Runs

```
jobRuns = myCdeClusterManager.listJobRuns()
json.loads(jobRuns)
```

#### Download Spark Event Logs

```
JOB_RUN_ID = "1"
logTypes = myCdeClusterManager.showAvailableLogTypes(JOB_RUN_ID)
json.loads(logTypes)

LOGS_TYPE = "driver/event"
sparkEventLogs = myCdeClusterManager.downloadJobRunLogs(JOB_RUN_ID, LOGS_TYPE)

sparkEventLogsClean = utils.sparkEventLogParser(sparkEventLogs)

print(sparkEventLogsClean)
```

#### Delete Job and Validate Deletion

```
CDE_JOB_NAME = "myCdeSparkJob"

myCdeClusterManager.deleteJob(CDE_JOB_NAME)

myCdeClusterManager.listJobs()
```

#### Describe Cluster Meta

```
myCdeClusterManager.describeResource(CDE_RESOURCE_NAME)
```

#### Remove Files from Files Resource

```
RESOURCE_FILE_NAME = "pysparksql.py"
myCdeClusterManager.removeFileFromResource(CDE_RESOURCE_NAME, RESOURCE_FILE_NAME)
```

#### Upload File to Resource

```
myCdeClusterManager.uploadFileToResource(CDE_RESOURCE_NAME, LOCAL_FILE_PATH, LOCAL_FILE_NAME)
```

#### Download File from Resource

```
myPySparkScript = myCdeClusterManager.downloadFileFromResource(CDE_RESOURCE_NAME, RESOURCE_FILE_NAME)

from pprint import pprint
pprint(myPySparkScript)
```

#### Pause Single Job

```
myCdeClusterManager.pauseSingleJob(CDE_JOB_NAME)
```

#### Delete Resource

```
CDE_RESOURCE_NAME = "myFilesCdeResource"

myCdeClusterManager.deleteResource(CDE_RESOURCE_NAME)
```


### CDE AIRFLOW PYTHON ENVIRONMENTS

NB: There is only one Airflow Python Environment per CDE Virtual Cluster.

```
from cdepy import cdeconnection
from cdepy import cdeairflowpython
import os
import json
```

#### Connect via CdeConnection Object

```
JOBS_API_URL = "<myJobsAPIurl>"
WORKLOAD_USER = "<myusername>"
WORKLOAD_PASSWORD = "<mypwd>"

myCdeConnection = cdeconnection.CdeConnection(JOBS_API_URL, WORKLOAD_USER, WORKLOAD_PASSWORD)

myCdeConnection.setToken()
```

#### Use CdeAirflowPythonEnv object to manage Airflow Python Environments

```
myAirflowPythonEnvManager = cdeairflowpython.CdeAirflowPythonEnv(myCdeConnection)
```

#### Create a Maintenance Session in order to perform any Airflow Python Environments related actions

```
myAirflowPythonEnvManager.createMaintenanceSession()
```

#### First Create a pip repository

```
myAirflowPythonEnvManager.createPipRepository()
```

#### Check on Status of Maintenance Session

```
myAirflowPythonEnvManager.checkAirflowPythonEnvStatus()
###### STATUS SHOULD BE {"status":"pip-repos-defined"}
```

#### Load requirements.txt file

```
pathToRequirementsTxt = "/examples/requirements.txt"
myAirflowPythonEnvManager.buildAirflowPythonEnv(pathToRequirementsTxt)
###### requirements.txt file must be customized

myAirflowPythonEnvManager.checkAirflowPythonEnvStatus()
###### RESPONSE STATUS SHOULD BE {"status":"building"}
###### AFTER 2 MINUTES REPEAT THE REQUEST. RESPONSE STATUS SHOULD EVENTUALLY BE {"status":"built"}
```

#### Validate status of Python environment

```
myAirflowPythonEnvManager.getAirflowPythonEnvironmentDetails()
```

#### Explore Maintenace Session logs

```
myAirflowPythonEnvManager.viewMaintenanceSessionLogs()
```

#### Activate the Python environment

```
myAirflowPythonEnvManager.activateAirflowPythonEnv()
```

#### Check on Python environment build status

```
myAirflowPythonEnvManager.checkAirflowPythonEnvStatus()
###### AT FIRST RESPONSE STATUS SHOULD BE {"status":"activating"}
###### AFTER A COUPLE OF MINUTES THE MAINTENANCE SESSION WILL AUTOMATICALLY END. THIS MEANS THE AIRFLOW PYTHON ENV HAS ACTIVATED.
```

#### Optional: Create a new session and then delete the Python environment

```
myAirflowPythonEnvManager.deleteAirflowPythonEnv()
```

#### Optional: End the Maintenance Session once you have deleted the Python environment

```
myAirflowPythonEnvManager.deleteMaintenanceSession()
```


### CDE REPOSITORIES

```
from cdepy import cdeconnection
from cdepy import cderepositories
import os
import json

JOBS_API_URL = "<myJobsAPIurl>"
WORKLOAD_USER = "<myusername>"
WORKLOAD_PASSWORD = "<mypwd>"
```

#### Connect via CdeConnection Object

```
myCdeConnection = cdeconnection.CdeConnection(JOBS_API_URL, WORKLOAD_USER, WORKLOAD_PASSWORD)
myCdeConnection.setToken()
```

#### Instantiate Repository Manager

```
myRepoManager = cderepositories.CdeRepositoryManager(myCdeConnection)
```

#### Provide example git repository information. This repository is available for tests.

```
repoName = "exampleGitRepository"
repoPath = "https://github.com/pdefusco/cde_git_repo.git"
```

#### Create CDE Repository from Git Repository

```
myRepoManager.createRepository(repoName, repoPath, repoBranch="main")
```

#### Show available CDE repositories

```
myRepoManager.listRepositories()
```

#### Show CDE Repository Metadata

```
myRepoManager.describeRepository(repoName)
```

#### Download file from CDE Repository

```
filePath = "simple-pyspark-sql.py"
myRepoManager.downloadFileFromRepo(repoName, filePath)
```

#### Sync CDE Repo with Origin

```
myRepoManager.syncRepository(repoName)
```

#### Delete CDE Repository

```
myRepoManager.deleteRepository(repoName)
```

#### Validate CDE Repository Deletion

```
myRepoManager.listRepositories()
```

#### Create a Basic Credential with Git Credentials

```
myCdeCredentialsManager = cdecredentials.CdeCredentialsManager(myCdeConnection)

credentialName = "myGitCredential"
credentialUsername = "<git-username>"
credentialPassword = "<git-token>"

myCdeCredentials = myCdeCredentialsManager.createBasicCredential(credentialName, credentialUsername, credentialPassword)

myCdeCredentialsManager.listCredentials()
```

#### Create a Repository with the Credential

```
myRepoManager = cderepositories.CdeRepositoryManager(myCdeConnection)

repoName = "examplePrivateRepository"
repoPath = "https://github.com/pdefusco/private_git_repo.git"

myRepoManager.createRepository(repoName, repoPath, repoCredentials=credentialName, repoBranch="main")

myRepoManager.listRepositories()

myRepoManager.describeRepository(repoName)
```
