## 🚀 ACDF-Agent-Bedrock: Automated Cloud Defense FinOps Agent

This repository contains the complete implementation strategy, code, and configuration required to deploy the **Automated Cloud Defense FinOps Agent (ACDF Agent)** using **Amazon Bedrock AgentCore**.

The ACDF Agent is designed to autonomously **detect, diagnose (via RAG), and remediate (via custom tool)** cloud cost anomalies.

### Key Features and Requirements Met:

| Feature | Execution Method | Requirement |
| :--- | :--- | :--- |
| **Orchestrator** | Amazon Bedrock AgentCore | **Mandatory** |
| **Tool-Use (API)** | `CostAnomalyChecker` Lambda querying a mock DynamoDB. | **Tool-Use** |
| **RAG/Knowledge Base** | Bedrock KB connected to "Internal Runbooks" (S3). | **RAG/KB** |
| **Advanced Tool-Use** | `NovaActExecutor` Lambda using the proprietary **Nova Act SDK** (mocked) to simulate complex UI-based triage. | **Nova Act Secret Weapon** |

-----

### 1\. Repository Structure

```
ACDF-Agent-Bedrock/
├── README.md                   
├── lambda-functions/
│   ├── CostAnomalyChecker/     <- Tool 1: Retrieves anomaly details from DynamoDB.
│   │   └── index.py            
│   ├── NovaActExecutor/        <- Tool 2: Executes Nova Act SDK (advanced triage).
│   │   └── index.py            
│   └── common/                 
├── data/
│   ├── dynamodb-mock-data.json <- Sample anomaly records for DynamoDB.
│   └── rag-runbooks/           <- RAG Documents (Internal Runbooks).
│       ├── S3-Anomaly-Runbook.txt
│       └── DynamoDB-Capacity-Runbook.txt
└── schemas/
    ├── CostAnomalyChecker-openapi.yaml  <- OpenAPI Schema for Tool 1.
    └── NovaActExecutor-openapi.yaml     <- OpenAPI Schema for Tool 2 (Nova Act).
```

-----

### 2\. Setup Instructions (Step-by-Step Guide)

Follow these steps to deploy all necessary components in your AWS account.

#### 2.1. Mock DynamoDB "Cost Anomaly" Setup

1.  **Create Table:** In the DynamoDB Console, create a table named **`CostAnomalies`**.
      * **Partition Key:** `AnomalyID` (String).
2.  **Mock Data Injection:** Use the data in `data/dynamodb-mock-data.json` to manually add at least one item. This item should include keys like `AnomalyID`, `ResourceARN`, `AnomalyType`, and `CostImpactUSD`.
      * *Example Item:* `AnomalyID: DB-001`, `ResourceARN: arn:aws:dynamodb:us-west-2:123456789012:table/MyHighCostTable`, `AnomalyType: DynamoDB-Capacity`.

#### 2.2. Bedrock Knowledge Base (RAG) Setup

1.  **S3 Bucket:** Create an S3 bucket (e.g., `acdf-runbooks-1234`).
2.  **Upload Documents:** Upload all files from the `data/rag-runbooks/` directory into this bucket.
3.  **Create KB:** In the Bedrock Console, create a new Knowledge Base:
      * **Data Source:** Point to the S3 URI of your runbooks bucket.
      * **Vector Store:** Choose **Quick setup** (uses OpenSearch Service Serverless).
      * Wait for the initial ingestion job to complete.

#### 2.3. Lambda Functions & IAM Configuration (Action Groups)

**A. Create Lambda Functions:** Create two Python 3.11+ Lambda functions.

1.  **`ACDF_CostAnomalyChecker`** (for Tool 1)
      * Paste code from `lambda-functions/CostAnomalyChecker/index.py`.
      * **IAM Policy:** Must have `dynamodb:GetItem` permission on the `CostAnomalies` table.
2.  **`ACDF_NovaActExecutor`** (for Advanced Tool 2)
      * Paste code from `lambda-functions/NovaActExecutor/index.py`.
      * **CRITICAL: Nova Act Mock:** The `index.py` file contains a mock implementation for the **Nova Act SDK**. It accepts the `resource_arn` and `triage_policy_name` and returns a success message, simulating the execution of a complex UI automation step (e.g., applying an IAM policy via the AWS Console UI).
      * **IAM Policy:** Must be granted permissions relevant to the action, e.g., `iam:AttachRolePolicy` and `iam:DetachRolePolicy` on resource ARNs.

**B. Upload OpenAPI Schemas:**

1.  Create an S3 bucket (e.g., `acdf-agent-schemas-1234`).
2.  Upload `schemas/CostAnomalyChecker-openapi.yaml` and `schemas/NovaActExecutor-openapi.yaml` to this S3 bucket.

#### 2.4. Amazon Bedrock AgentCore Configuration

1.  **Create Agent:** In the Bedrock Console, create a new Agent.

      * **Model:** Use a powerful model like **Anthropic Claude 3 Sonnet**.
      * **Agent Instruction (CRITICAL):**
        > "You are the ACDF FinOps Agent. Your goal is to detect, diagnose, and remediate cost anomalies. You MUST follow this process: 1. Use the `CostAnomalyChecker` tool to get anomaly details. 2. Consult the **Internal Runbooks** (Knowledge Base) to diagnose the required `triage_policy_name` based on the `anomaly_type`. 3. Finally, use the `NovaActTriageTool` to apply the triage."

2.  **Add Knowledge Base:** Attach the KB created in Step 2.2.

3.  **Add Action Groups:** Attach the two Lambda functions as Action Groups, pointing to the S3 locations of their respective OpenAPI schemas.

| Action Group Name | Lambda ARN | API Schema S3 Location |
| :--- | :--- | :--- |
| `CostAnomalyChecker` | ARN of `ACDF_CostAnomalyChecker` | S3 URI of `CostAnomalyChecker-openapi.yaml` |
| `NovaActTriageTool` | ARN of `ACDF_NovaActExecutor` | S3 URI of `NovaActExecutor-openapi.yaml` |

-----

### 3\. OpenAPI Schemas

The agent uses these schemas for planning and tool selection.

#### 3.1. `schemas/CostAnomalyChecker-openapi.yaml`

```yaml
# Content from the file (refer to the repository)
openapi: 3.0.0
info:
  title: Cost Anomaly Checker API
  version: '1.0'
paths:
  /getAnomalyDetails:
    post:
      summary: Retrieves detailed information about a specific cloud cost anomaly from the database.
      operationId: get_anomaly_details
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                anomaly_id:
                  type: string
                  description: The unique identifier of the cost anomaly (e.g., 'DB-001').
              required:
                - anomaly_id
      responses:
        '200':
          description: Cost anomaly details successfully retrieved.
          content:
            application/json:
              schema:
                type: object
                properties:
                  resource_arn:
                    type: string
                    description: The ARN of the AWS resource causing the anomaly.
                  anomaly_type:
                    type: string
                    description: The service type of the anomaly (e.g., 'DynamoDB-Capacity', 'S3-HighOps').
                  cost_impact_usd:
                    type: number
                    description: The estimated cost impact in USD.
```

#### 3.2. `schemas/NovaActExecutor-openapi.yaml`

```yaml
# Content from the file (refer to the repository)
openapi: 3.0.0
info:
  title: Nova Act SDK Executor for Cloud Triage
  version: '1.0'
paths:
  /applyTriagePolicy:
    post:
      summary: Executes the Nova Act SDK to apply a temporary restrictive IAM policy via the AWS Console UI automation for resource triage.
      description: This is a highly privileged, non-API operation that simulates UI interaction for sensitive actions. The agent should only call this after diagnosis via RAG.
      operationId: apply_triage_policy
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                resource_arn:
                  type: string
                  description: The ARN of the anomalous resource requiring immediate policy triage.
                triage_policy_name:
                  type: string
                  description: The name of the temporary policy to apply (e.g., 'Restrict_Write_Access').
              required:
                - resource_arn
                - triage_policy_name
      responses:
        '200':
          description: Triage policy applied successfully via Nova Act SDK automation.
```

### 4\. Sample RAG Documents (Internal Runbooks)

These documents are key for the diagnosis step. The agent must retrieve the correct `triage_policy_name` from these files.

#### 4.1. `data/rag-runbooks/S3-Anomaly-Runbook.txt`

```
INTERNAL RUNBOOK: S3-HighOps Anomaly Remediation
...
Triage Plan (Required Action):
...
2. Use the NovaActExecutor (apply_triage_policy) tool to apply the 'Restrict_Write_Access' policy to the S3 bucket's access point immediately.
...
```

#### 4.2. `data/rag-runbooks/DynamoDB-Capacity-Runbook.txt`

```
INTERNAL RUNBOOK: DynamoDB-Capacity Anomaly Remediation
...
Triage Plan (Required Action):
...
3. If auto-scaling is DISABLED: Use the NovaActExecutor (apply_triage_policy) tool to apply the 'Limit_Capacity_To_Base' policy to the table's IAM execution role to halt aggressive scaling until manual review.
```

### 5\. Testing the Agent

1.  Navigate to the **Test** section of your Bedrock Agent in the AWS Console.
2.  **Test Prompt (Full Workflow):**
    > "A high-cost alert for **AnomalyID 'DB-001'** was just triggered. Please perform the full diagnosis and triage."

**Expected Agent Behavior (Trace):**

1.  **Plan:** Bedrock Agent identifies the need to call `CostAnomalyChecker.get_anomaly_details(anomaly_id='DB-001')`.
2.  **Tool 1 Execution:** Lambda runs, returns details (e.g., `anomaly_type: DynamoDB-Capacity`, `resource_arn: ...`).
3.  **RAG/Diagnosis:** Agent queries the Knowledge Base with `AnomalyType: DynamoDB-Capacity` to find the corresponding runbook.
4.  **RAG Output:** Agent reads the Runbook and identifies the required action: `triage_policy_name: Limit_Capacity_To_Base`.
5.  **Plan:** Agent identifies the need to call the advanced tool `NovaActTriageTool.apply_triage_policy(resource_arn='...', triage_policy_name='Limit_Capacity_To_Base')`.
6.  **Tool 2 Execution:** Lambda runs, simulates the successful UI automation via the Nova Act SDK, and returns a success message.
7.  **Final Response:** Agent synthesizes the diagnosis and successful remediation steps to the user.
