import os
import azureml.core
from azureml.core.authentication import ServicePrincipalAuthentication

from azureml.core import (
    Workspace,
    Experiment,
    Dataset,
    Datastore,
    ComputeTarget,
    Environment,
    ScriptRunConfig
)

print("- SDK version:", azureml.core.VERSION)


## 작업 영역 연결 ##

svc_pr= ServicePrincipalAuthentication(
    tenant_id="247258cc-5eb2-4fd4-9bb2-f272103f0c34",
    service_principal_id="b7cfba68-a51b-4ae3-8885-cef273960a5e",
    service_principal_password="d4f8Q~~8tUXmQelSJyquy7lys17-t8gecKXCrb47")


ws = Workspace.get(subscription_id="7722d447-2b14-4ca2-83c1-b4df9454a55a",
                    resource_group="MLOps_POC",
                    name="mlw-mlops-dev-002",
                    auth=svc_pr)

print("- Workspace Connection success.\n")
print(ws.name, ws.resource_group, ws.subscription_id, sep = '\n')

## Experiment ##
experiment_folder = 'python_pipeline'
os.makedirs(experiment_folder, exist_ok = True)

print("- Experiment Folder is :",experiment_folder)

# # choose a name for your cluster ##
# cluster_name = "cluster-mlops-jh"

# print("- Cluster name is :",cluster_name)

## environment 생성 및 등록 ##
experiment_env = Environment.from_conda_specification("PV_env_test", "src/" + experiment_folder + "/conda.yml")
experiment_env.register(workspace=ws)
print("- Environment Register success.\n")