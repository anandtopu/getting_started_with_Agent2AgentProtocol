# Protocol guide

A2A 1.0.1 uses one normative protobuf schema across JSON-RPC, HTTP+JSON and gRPC. The tables below are generated from the installed 1.3.0 SDK descriptor, checked against the versioned protocol definition.

## Follow one request

1. Fetch the Agent Card at /.well-known/agent-card.json.
2. Choose a supported interface and obtain its required credentials separately.
3. Send a Message inside SendMessageRequest with A2A-Version: 1.0.
4. Receive a Message or a Task. For a task, preserve its IDs and inspect status and artifacts.
5. If interrupted, provide the missing input or obtain authorization outside the message payload.
6. Treat completed, failed, canceled and rejected tasks as terminal.

## Operations

| Operation | Request | Response | Form |
|---|---|---|---|
| SendMessage | SendMessageRequest | SendMessageResponse | unary |
| SendStreamingMessage | SendMessageRequest | StreamResponse | stream |
| GetTask | GetTaskRequest | Task | unary |
| ListTasks | ListTasksRequest | ListTasksResponse | unary |
| CancelTask | CancelTaskRequest | Task | unary |
| SubscribeToTask | SubscribeToTaskRequest | StreamResponse | stream |
| CreateTaskPushNotificationConfig | TaskPushNotificationConfig | TaskPushNotificationConfig | unary |
| GetTaskPushNotificationConfig | GetTaskPushNotificationConfigRequest | TaskPushNotificationConfig | unary |
| ListTaskPushNotificationConfigs | ListTaskPushNotificationConfigsRequest | ListTaskPushNotificationConfigsResponse | unary |
| GetExtendedAgentCard | GetExtendedAgentCardRequest | AgentCard | unary |
| DeleteTaskPushNotificationConfig | DeleteTaskPushNotificationConfigRequest | Empty | unary |

## Objects and exact JSON fields

| Object | JSON fields |
|---|---|
| SendMessageConfiguration | acceptedOutputModes, taskPushNotificationConfig, historyLength, returnImmediately |
| Task | id, contextId, status, artifacts, history, metadata |
| TaskStatus | state, message, timestamp |
| Part | text, raw, url, data, metadata, filename, mediaType |
| Message | messageId, contextId, taskId, role, parts, metadata, extensions, referenceTaskIds |
| Artifact | artifactId, name, description, parts, metadata, extensions |
| TaskStatusUpdateEvent | taskId, contextId, status, metadata |
| TaskArtifactUpdateEvent | taskId, contextId, artifact, append, lastChunk, metadata |
| AuthenticationInfo | scheme, credentials |
| AgentInterface | url, protocolBinding, tenant, protocolVersion |
| AgentCard | name, description, supportedInterfaces, provider, version, documentationUrl, capabilities, securitySchemes, securityRequirements, defaultInputModes, defaultOutputModes, skills, signatures, iconUrl |
| AgentProvider | url, organization |
| AgentCapabilities | streaming, pushNotifications, extensions, extendedAgentCard |
| AgentExtension | uri, description, required, params |
| AgentSkill | id, name, description, tags, examples, inputModes, outputModes, securityRequirements |
| AgentCardSignature | protected, signature, header |
| TaskPushNotificationConfig | tenant, id, taskId, url, token, authentication |
| StringList | list |
| SecurityRequirement | schemes |
| SecurityScheme | apiKeySecurityScheme, httpAuthSecurityScheme, oauth2SecurityScheme, openIdConnectSecurityScheme, mtlsSecurityScheme |
| APIKeySecurityScheme | description, location, name |
| HTTPAuthSecurityScheme | description, scheme, bearerFormat |
| OAuth2SecurityScheme | description, flows, oauth2MetadataUrl |
| OpenIdConnectSecurityScheme | description, openIdConnectUrl |
| MutualTlsSecurityScheme | description |
| OAuthFlows | authorizationCode, clientCredentials, implicit, password, deviceCode |
| AuthorizationCodeOAuthFlow | authorizationUrl, tokenUrl, refreshUrl, scopes, pkceRequired |
| ClientCredentialsOAuthFlow | tokenUrl, refreshUrl, scopes |
| ImplicitOAuthFlow | authorizationUrl, refreshUrl, scopes |
| PasswordOAuthFlow | tokenUrl, refreshUrl, scopes |
| DeviceCodeOAuthFlow | deviceAuthorizationUrl, tokenUrl, refreshUrl, scopes |
| SendMessageRequest | tenant, message, configuration, metadata |
| GetTaskRequest | tenant, id, historyLength |
| ListTasksRequest | tenant, contextId, status, pageSize, pageToken, historyLength, statusTimestampAfter, includeArtifacts |
| ListTasksResponse | tasks, nextPageToken, pageSize, totalSize |
| CancelTaskRequest | tenant, id, metadata |
| GetTaskPushNotificationConfigRequest | tenant, taskId, id |
| DeleteTaskPushNotificationConfigRequest | tenant, taskId, id |
| SubscribeToTaskRequest | tenant, id |
| ListTaskPushNotificationConfigsRequest | tenant, taskId, pageSize, pageToken |
| GetExtendedAgentCardRequest | tenant |
| SendMessageResponse | task, message |
| StreamResponse | task, message, statusUpdate, artifactUpdate |
| ListTaskPushNotificationConfigsResponse | configs, nextPageToken |

## Actual examples

- [JSON-RPC request and response](../modules/01_how_a2a_works/wire/01_jsonrpc.jsonl)
- [HTTP+JSON](../modules/08_bindings/wire/02_rest.jsonl)
- [Protobuf service boundary](../modules/08_bindings/wire/03_grpc.jsonl)
- [SSE events](../modules/07_streaming_push/wire/01_stream.jsonl)
- [Push configuration and deliveries](../modules/07_streaming_push/wire/03_push.jsonl)
- [Task continuation](../modules/05_task_lifecycle/wire/02_resume.jsonl)

These captures cover the implemented labs, not every possible object or operation variant.

Sources: [normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto), [binding rules](https://a2a-protocol.org/v1.0.1/specification/).
