package cloudify

import (
	"cloudify/rest"
	"encoding/json"
	"log"
)

type CloudifyExecutionPost struct {
	WorkflowId   string `json:"workflow_id"`
	DeploymentId string `json:"deployment_id"`
}

type CloudifyExecution struct {
	// can be response from api
	rest.CloudifyBaseMessage
	// have id, owner information
	rest.CloudifyResource
	// contain information from post
	CloudifyExecutionPost
	IsSystemWorkflow bool   `json:"is_system_workflow"`
	Error            string `json:"error"`
	BlueprintId      string `json:"blueprint_id"`
	Status           string `json:"status"`
	// TODO describe "parameters" struct
}

type CloudifyExecutions struct {
	rest.CloudifyBaseMessage
	Metadata rest.CloudifyMetadata `json:"metadata"`
	Items    []CloudifyExecution   `json:"items"`
}

func GetExecutions(host, user, password, tenant string) CloudifyExecutions {
	body := rest.Get("http://"+host+"/api/v3.1/executions", user, password, tenant)

	var executions CloudifyExecutions

	err := json.Unmarshal(body, &executions)
	if err != nil {
		log.Fatal(err)
	}

	if len(executions.ErrorCode) > 0 {
		log.Fatal(executions.Message)
	}

	return executions
}

func PostExecution(host, user, password, tenant string, exec CloudifyExecutionPost) CloudifyExecution {
	json_data, err := json.Marshal(exec)
	if err != nil {
		log.Fatal(err)
	}

	body := rest.Post("http://"+host+"/api/v3.1/executions", user, password, tenant, json_data)

	var execution CloudifyExecution

	err_post := json.Unmarshal(body, &execution)
	if err_post != nil {
		log.Fatal(err_post)
	}

	if len(execution.ErrorCode) > 0 {
		log.Fatal(execution.Message)
	}

	return execution
}