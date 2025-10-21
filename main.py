The next things to add to the GitHub repository, following the comprehensive `README.md`, are the actual **code files** and the **data files** necessary for the project to be functional and deployable.

Here is a plan outlining the content for each file based on the established structure:

-----

## 1\. Lambda Function Code Files (`lambda-functions/`)

These files contain the business logic invoked by the Bedrock Agent's Action Groups.

### 1.1. `lambda-functions/CostAnomalyChecker/index.py` (Tool 1 - DynamoDB)

This script will mock a DynamoDB query to return a structured JSON response.

```python
import json
import boto3
import os

# --- Mock Data Setup (In a real scenario, this would be a live DynamoDB call) ---
def mock_dynamodb_query(anomaly_id):
    # This data simulates the output of a DynamoDB GetItem call
    # The agent expects to get the ResourceARN and AnomalyType to feed into the RAG step.
    mock_data = {
        "DB-001": {
            "ResourceARN": "arn:aws:dynamodb:us-west-2:123456789012:table/HighCostTableA",
            "AnomalyType": "DynamoDB-Capacity",
            "CostImpactUSD": 450.75,
            "Service": "DynamoDB"
        },
        "S3-005": {
            "ResourceARN": "arn:aws:s3:::customer-data-lake-prod",
            "AnomalyType": "S3-HighOps",
            "CostImpactUSD": 980.50,
            "Service": "S3"
        }
    }
    return mock_data.get(anomaly_id, {"Error": "Anomaly not found"})

# --- Main Lambda Handler ---
def lambda_handler(event, context):
    try:
        # Bedrock Agent sends the action group payload in the 'body'
        event_body = json.loads(event['body'])
        
        # Action ID defined in the OpenAPI schema
        action_name = event['actionGroup']
        
        # The function defined in the OpenAPI schema
        function_name = event['function']

        if function_name == 'get_anomaly_details':
            # Extract parameter from the payload
            anomaly_id = event_body.get('anomaly_id')
            if not anomaly_id:
                return {'body': json.dumps({'error': 'Missing required parameter: anomaly_id'})}

            anomaly_details = mock_dynamodb_query(anomaly_id)

            if "Error" in anomaly_details:
                 return {'body': json.dumps({'result': f"ERROR: {anomaly_details['Error']}"})}

            # Return the details in a format the agent can understand for subsequent steps (RAG)
            return {
                'body': json.dumps({
                    "details": f"Anomaly found: ResourceARN={anomaly_details['ResourceARN']}, Type={anomaly_details['AnomalyType']}, Impact={anomaly_details['CostImpactUSD']}"
                })
            }

        return {'body': json.dumps({'error': f"Unknown function: {function_name}"})}

    except Exception as e:
        print(f"Error processing request: {e}")
        return {'body': json.dumps({'error': str(e)})}
```

### 1.2. `lambda-functions/NovaActExecutor/index.py` (Tool 2 - Nova Act SDK Mock)

This script simulates the execution of the advanced, proprietary Nova Act SDK after the agent has diagnosed the necessary action using RAG.

```python
import json
import time # Used to simulate a long-running UI automation task

# --- Mock Nova Act SDK Function (The Secret Weapon) ---
def invoke_nova_act_sdk(resource_arn, policy_name):
    """
    Mocks the complex UI automation interaction performed by the Nova Act SDK.
    This simulates applying a restrictive IAM policy via a non-API-accessible
    interface in the AWS console, which is crucial for the advanced tool requirement.
    """
    print(f"Nova Act SDK: Initiating UI automation for resource: {resource_arn}")
    time.sleep(2) # Simulate execution delay
    
    # In a real scenario, this would be a call to a third-party service/SDK
    # NovaActSDK.apply_policy(arn=resource_arn, policy=policy_name)
    
    return {
        "status": "SUCCESS",
        "message": f"Nova Act SDK successfully executed complex UI automation: Policy '{policy_name}' has been temporarily applied to the resource or its associated role/user ({resource_arn}) for triage."
    }

# --- Main Lambda Handler ---
def lambda_handler(event, context):
    try:
        event_body = json.loads(event['body'])
        action_name = event['actionGroup']
        function_name = event['function']

        if function_name == 'apply_triage_policy':
            # Extract parameters from the payload, as determined by the Agent's reasoning
            resource_arn = event_body.get('resource_arn')
            policy_name = event_body.get('triage_policy_name')

            if not resource_arn or not policy_name:
                return {'body': json.dumps({'error': 'Missing required parameters for triage.'})}

            result = invoke_nova_act_sdk(resource_arn, policy_name)

            # Return a clear message back to the agent for final synthesis
            return {
                'body': json.dumps(result)
            }

        return {'body': json.dumps({'error': f"Unknown function: {function_name}"})}

    except Exception as e:
        print(f"Error processing Nova Act request: {e}")
        return {'body': json.dumps({'error': str(e)})}
```

-----

## 2\. Data Files (`data/`)

### 2.1. `data/dynamodb-mock-data.json` (for DynamoDB Mock)

This file provides the structured data for the `CostAnomalyChecker` to retrieve.

```json
[
  {
    "AnomalyID": {"S": "DB-001"},
    "ResourceARN": {"S": "arn:aws:dynamodb:us-west-2:123456789012:table/HighCostTableA"},
    "AnomalyType": {"S": "DynamoDB-Capacity"},
    "CostImpactUSD": {"N": "450.75"},
    "Description": {"S": "Uncontrolled read capacity spike."}
  },
  {
    "AnomalyID": {"S": "S3-005"},
    "ResourceARN": {"S": "arn:aws:s3:::customer-data-lake-prod"},
    "AnomalyType": {"S": "S3-HighOps"},
    "CostImpactUSD": {"N": "980.50"},
    "Description": {"S": "High PUT/LIST volume due to client misconfiguration."}
  }
]
```

### 2.2. RAG Documents (`data/rag-runbooks/`)

*The content of these files was detailed in the previous response and should be included as separate `.txt` files in the repository.*

-----

## 3\. Schemas (`schemas/`)

*The content of these OpenAPI YAML files was detailed in the previous response and should be included as separate `.yaml` files in the repository.*

### 3.1. `schemas/CostAnomalyChecker-openapi.yaml`

### 3.2. `schemas/NovaActExecutor-openapi.yaml`

-----

**Summary of Next Steps:**

1.  Create the directory structure as planned.
2.  Populate the two Python files in `lambda-functions/`.
3.  Populate the `dynamodb-mock-data.json` file.
4.  Populate the two OpenAPI YAML files in `schemas/`.
5.  Populate the two internal runbook files in `data/rag-runbooks/`.
