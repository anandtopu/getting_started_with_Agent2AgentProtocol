# Every operation on the wire

These are captured SDK 1.3.0 exchanges targeting A2A 1.0.1. Generated IDs vary.
Regenerate with uv run python scripts/capture_operations.py and then this script.
Credentials were redacted before writing. gRPC captures are protobuf service calls,
not HTTP/2 packet captures. The live gRPC network is tested separately.

[JSON-RPC records](wire/jsonrpc-operations.jsonl) · [HTTP+JSON records](wire/http_json-operations.jsonl) · [gRPC records](wire/grpc-operations.jsonl)

## SendMessage

Hand a vendor a brief. The result can be a Message or a tracked Task; do not assume every response has artifacts.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: POST http://127.0.0.1:8101/message:send

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "SendMessage",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "0576def0-c27e-4e0e-b526-783882e45942",
      "role": "ROLE_USER",
      "parts": [
        {
          "data": {
            "guests": 40.0
          },
          "mediaType": "application/json"
        }
      ]
    }
  }
}
~~~

Actual response:
~~~json
{
  "result": {
    "task": {
      "id": "8db6c61a-22af-4aff-a364-34673230fd83",
      "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
      "status": {
        "state": "TASK_STATE_INPUT_REQUIRED",
        "message": {
          "messageId": "55475bb6-b65e-4a61-9b41-2fe0421a1625",
          "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
          "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
          "role": "ROLE_AGENT",
          "parts": [
            {
              "text": "How many guests need each dietary option?"
            }
          ]
        }
      },
      "history": [
        {
          "messageId": "0576def0-c27e-4e0e-b526-783882e45942",
          "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
          "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
          "role": "ROLE_USER",
          "parts": [
            {
              "data": {
                "guests": 40.0
              },
              "mediaType": "application/json"
            }
          ]
        },
        {
          "messageId": "0dff5d63-11f1-4132-84da-b6700206d7ab",
          "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
          "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
          "role": "ROLE_AGENT",
          "parts": [
            {
              "text": "catering: checking the brief"
            }
          ]
        }
      ],
      "metadata": {
        "brief": {
          "guests": 40.0
        }
      }
    }
  },
  "id": "SendMessage",
  "jsonrpc": "2.0"
}
~~~

## GetTask

Read a work order by its server-assigned ID. Ownership checks still apply; knowing an ID does not grant access.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: GET http://127.0.0.1:8101/tasks/30ba8a31-e1eb-44c0-8641-fc0a3f7f331d?historyLength=1

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "GetTask",
  "method": "GetTask",
  "params": {
    "id": "8db6c61a-22af-4aff-a364-34673230fd83",
    "historyLength": 1
  }
}
~~~

Actual response:
~~~json
{
  "result": {
    "id": "8db6c61a-22af-4aff-a364-34673230fd83",
    "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
    "status": {
      "state": "TASK_STATE_INPUT_REQUIRED",
      "message": {
        "messageId": "55475bb6-b65e-4a61-9b41-2fe0421a1625",
        "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
        "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
        "role": "ROLE_AGENT",
        "parts": [
          {
            "text": "How many guests need each dietary option?"
          }
        ]
      }
    },
    "history": [
      {
        "messageId": "0dff5d63-11f1-4132-84da-b6700206d7ab",
        "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
        "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
        "role": "ROLE_AGENT",
        "parts": [
          {
            "text": "catering: checking the brief"
          }
        ]
      }
    ],
    "metadata": {
      "brief": {
        "guests": 40.0
      }
    }
  },
  "id": "GetTask",
  "jsonrpc": "2.0"
}
~~~

## ListTasks

Read a page of work orders. Treat nextPageToken as opaque, and preserve the filter choices for the next request.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: GET http://127.0.0.1:8101/tasks?pageSize=1&includeArtifacts=true

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "ListTasks",
  "method": "ListTasks",
  "params": {
    "pageSize": 1,
    "includeArtifacts": true
  }
}
~~~

Actual response:
~~~json
{
  "result": {
    "tasks": [
      {
        "id": "8db6c61a-22af-4aff-a364-34673230fd83",
        "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
        "status": {
          "state": "TASK_STATE_INPUT_REQUIRED",
          "message": {
            "messageId": "55475bb6-b65e-4a61-9b41-2fe0421a1625",
            "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
            "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
            "role": "ROLE_AGENT",
            "parts": [
              {
                "text": "How many guests need each dietary option?",
                "filename": "",
                "mediaType": ""
              }
            ],
            "extensions": [],
            "referenceTaskIds": []
          }
        },
        "history": [
          {
            "messageId": "0576def0-c27e-4e0e-b526-783882e45942",
            "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
            "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
            "role": "ROLE_USER",
            "parts": [
              {
                "data": {
                  "guests": 40.0
                },
                "mediaType": "application/json",
                "filename": ""
              }
            ],
            "extensions": [],
            "referenceTaskIds": []
          },
          {
            "messageId": "0dff5d63-11f1-4132-84da-b6700206d7ab",
            "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
            "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
            "role": "ROLE_AGENT",
            "parts": [
              {
                "text": "catering: checking the brief",
                "filename": "",
                "mediaType": ""
              }
            ],
            "extensions": [],
            "referenceTaskIds": []
          }
        ],
        "metadata": {
          "brief": {
            "guests": 40.0
          }
        },
        "artifacts": []
      }
    ],
    "pageSize": 1,
    "totalSize": 1,
    "nextPageToken": ""
  },
  "id": "ListTasks",
  "jsonrpc": "2.0"
}
~~~

## CreateTaskPushNotificationConfig

Register a callback destination for one task. The server checks its destination policy before accepting it.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: POST http://127.0.0.1:8101/tasks/30ba8a31-e1eb-44c0-8641-fc0a3f7f331d/pushNotificationConfigs

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "CreateTaskPushNotificationConfig",
  "method": "CreateTaskPushNotificationConfig",
  "params": {
    "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
    "id": "capture",
    "url": "https://callback.maplewood.example/notify"
  }
}
~~~

Actual response:
~~~json
{
  "result": {
    "id": "capture",
    "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
    "url": "https://callback.maplewood.example/notify"
  },
  "id": "CreateTaskPushNotificationConfig",
  "jsonrpc": "2.0"
}
~~~

## GetTaskPushNotificationConfig

Read one callback registration using both task and configuration IDs.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: GET http://127.0.0.1:8101/tasks/30ba8a31-e1eb-44c0-8641-fc0a3f7f331d/pushNotificationConfigs/capture

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "GetTaskPushNotificationConfig",
  "method": "GetTaskPushNotificationConfig",
  "params": {
    "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
    "id": "capture"
  }
}
~~~

Actual response:
~~~json
{
  "result": {
    "id": "capture",
    "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
    "url": "https://callback.maplewood.example/notify"
  },
  "id": "GetTaskPushNotificationConfig",
  "jsonrpc": "2.0"
}
~~~

## ListTaskPushNotificationConfigs

Inspect all callback registrations for a task, subject to the same task-owner authorization.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: GET http://127.0.0.1:8101/tasks/30ba8a31-e1eb-44c0-8641-fc0a3f7f331d/pushNotificationConfigs

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "ListTaskPushNotificationConfigs",
  "method": "ListTaskPushNotificationConfigs",
  "params": {
    "taskId": "8db6c61a-22af-4aff-a364-34673230fd83"
  }
}
~~~

Actual response:
~~~json
{
  "result": {
    "configs": [
      {
        "id": "capture",
        "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
        "url": "https://callback.maplewood.example/notify"
      }
    ]
  },
  "id": "ListTaskPushNotificationConfigs",
  "jsonrpc": "2.0"
}
~~~

## DeleteTaskPushNotificationConfig

Remove a callback registration. A successful empty response does not mean the task itself was canceled.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: DELETE http://127.0.0.1:8101/tasks/30ba8a31-e1eb-44c0-8641-fc0a3f7f331d/pushNotificationConfigs/capture

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "DeleteTaskPushNotificationConfig",
  "method": "DeleteTaskPushNotificationConfig",
  "params": {
    "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
    "id": "capture"
  }
}
~~~

Actual response:
~~~json
{
  "result": null,
  "id": "DeleteTaskPushNotificationConfig",
  "jsonrpc": "2.0"
}
~~~

## GetExtendedAgentCard

Request an authenticated partner view. A public card does not automatically authorize this operation.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: GET http://127.0.0.1:8101/extendedAgentCard

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "GetExtendedAgentCard",
  "method": "GetExtendedAgentCard",
  "params": {}
}
~~~

Actual response:
~~~json
{
  "result": {
    "name": "Saffron Table Catering",
    "description": "Quote a menu for a guest count and dietary breakdown; ask for missing dietary counts. No purchase.",
    "supportedInterfaces": [
      {
        "url": "http://127.0.0.1:8101/rpc",
        "protocolBinding": "JSONRPC",
        "protocolVersion": "1.0"
      },
      {
        "url": "http://127.0.0.1:8101",
        "protocolBinding": "HTTP+JSON",
        "protocolVersion": "1.0"
      }
    ],
    "provider": {
      "url": "https://maplewood.example",
      "organization": "Saffron Table Catering"
    },
    "version": "1.0.0",
    "capabilities": {
      "streaming": true,
      "pushNotifications": true,
      "extensions": [
        {
          "uri": "https://maplewood.example/extensions/structured-quote/v1"
        }
      ],
      "extendedAgentCard": true
    },
    "securitySchemes": {
      "vendor_token": {
        "httpAuthSecurityScheme": {
          "scheme": "Bearer"
        }
      }
    },
    "securityRequirements": [
      {
        "schemes": {
          "vendor_token": {}
        }
      }
    ],
    "defaultInputModes": [
      "text/plain",
      "application/json",
      "application/octet-stream"
    ],
    "defaultOutputModes": [
      "application/json",
      "text/plain"
    ],
    "skills": [
      {
        "id": "catering.quote",
        "name": "Saffron Table Catering quote",
        "description": "Quote a menu for a guest count and dietary breakdown; ask for missing dietary counts. No purchase.",
        "tags": [
          "events",
          "catering"
        ],
        "examples": [
          "Quote a 40-person offsite on 2027-06-01"
        ]
      }
    ]
  },
  "id": "GetExtendedAgentCard",
  "jsonrpc": "2.0"
}
~~~

## CancelTask

Ask a vendor to stop unfinished work. This does not undo a completed reservation or payment.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: POST http://127.0.0.1:8101/tasks/30ba8a31-e1eb-44c0-8641-fc0a3f7f331d:cancel

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "CancelTask",
  "method": "CancelTask",
  "params": {
    "id": "8db6c61a-22af-4aff-a364-34673230fd83"
  }
}
~~~

Actual response:
~~~json
{
  "result": {
    "id": "8db6c61a-22af-4aff-a364-34673230fd83",
    "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
    "status": {
      "state": "TASK_STATE_CANCELED",
      "message": {
        "messageId": "c992c89e-1f8e-4cfd-812c-2ddf53baec55",
        "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
        "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
        "role": "ROLE_AGENT",
        "parts": [
          {
            "text": "Work canceled. No booking was made."
          }
        ]
      }
    },
    "history": [
      {
        "messageId": "0576def0-c27e-4e0e-b526-783882e45942",
        "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
        "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
        "role": "ROLE_USER",
        "parts": [
          {
            "data": {
              "guests": 40.0
            },
            "mediaType": "application/json"
          }
        ]
      },
      {
        "messageId": "0dff5d63-11f1-4132-84da-b6700206d7ab",
        "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
        "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
        "role": "ROLE_AGENT",
        "parts": [
          {
            "text": "catering: checking the brief"
          }
        ]
      },
      {
        "messageId": "55475bb6-b65e-4a61-9b41-2fe0421a1625",
        "contextId": "f6f68200-1bfd-43f6-b8a7-f91e547b744c",
        "taskId": "8db6c61a-22af-4aff-a364-34673230fd83",
        "role": "ROLE_AGENT",
        "parts": [
          {
            "text": "How many guests need each dietary option?"
          }
        ]
      }
    ],
    "metadata": {
      "brief": {
        "guests": 40.0
      }
    }
  },
  "id": "CancelTask",
  "jsonrpc": "2.0"
}
~~~

## SubscribeToTask

Reconnect to active work. This capture intentionally attempts a terminal task and records the real unsupported-operation error.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: GET http://127.0.0.1:8101/tasks/30ba8a31-e1eb-44c0-8641-fc0a3f7f331d:subscribe

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "SubscribeToTask",
  "method": "SubscribeToTask",
  "params": {
    "id": "8db6c61a-22af-4aff-a364-34673230fd83"
  }
}
~~~

Actual response:
~~~json
{
  "error": {
    "code": -32004,
    "message": "Task 8db6c61a-22af-4aff-a364-34673230fd83 is in terminal state: TASK_STATE_CANCELED",
    "data": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "UNSUPPORTED_OPERATION",
        "domain": "a2a-protocol.org",
        "metadata": {}
      }
    ]
  },
  "id": "SubscribeToTask",
  "jsonrpc": "2.0"
}
~~~

## SendStreamingMessage

Open a stream of task snapshots, status updates and artifact updates. Read the wrapper member to identify each event.

[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

HTTP+JSON: POST http://127.0.0.1:8101/message:stream

JSON-RPC request:
~~~json
{
  "jsonrpc": "2.0",
  "id": "SendStreamingMessage",
  "method": "SendStreamingMessage",
  "params": {
    "message": {
      "messageId": "a32a9a32-8e58-48f8-b5fa-9b025df52e9b",
      "role": "ROLE_USER",
      "parts": [
        {
          "data": {
            "dietary": {
              "vegan": 40.0
            },
            "guests": 40.0
          },
          "mediaType": "application/json"
        }
      ]
    }
  }
}
~~~

Actual response:
~~~json
"data: {\"result\": {\"task\": {\"id\": \"5fa79b82-8f2f-4fbf-b9a2-191a80e1edde\", \"contextId\": \"8b94add6-23e8-4367-b98d-5a23fe5e37e6\", \"status\": {\"state\": \"TASK_STATE_SUBMITTED\"}, \"history\": [{\"messageId\": \"a32a9a32-8e58-48f8-b5fa-9b025df52e9b\", \"contextId\": \"8b94add6-23e8-4367-b98d-5a23fe5e37e6\", \"taskId\": \"5fa79b82-8f2f-4fbf-b9a2-191a80e1edde\", \"role\": \"ROLE_USER\", \"parts\": [{\"data\": {\"guests\": 40.0, \"dietary\": {\"vegan\": 40.0}}, \"mediaType\": \"application/json\"}]}], \"metadata\": {\"brief\": {\"dietary\": {\"vegan\": 40.0}, \"guests\": 40.0}}}}, \"id\": \"SendStreamingMessage\", \"jsonrpc\": \"2.0\"}\r\n\r\ndata: {\"result\": {\"statusUpdate\": {\"taskId\": \"5fa79b82-8f2f-4fbf-b9a2-191a80e1edde\", \"contextId\": \"8b94add6-23e8-4367-b98d-5a23fe5e37e6\", \"status\": {\"state\": \"TASK_STATE_WORKING\", \"message\": {\"messageId\": \"d8acd07f-1642-471d-bd7f-978ed0b007d9\", \"contextId\": \"8b94add6-23e8-4367-b98d-5a23fe5e37e6\", \"taskId\": \"5fa79b82-8f2f-4fbf-b9a2-191a80e1edde\", \"role\": \"ROLE_AGENT\", \"parts\": [{\"text\": \"catering: checking the brief\"}]}}}}, \"id\": \"SendStreamingMessage\", \"jsonrpc\": \"2.0\"}\r\n\r\ndata: {\"result\": {\"artifactUpdate\": {\"taskId\": \"5fa79b82-8f2f-4fbf-b9a2-191a80e1edde\", \"contextId\": \"8b94add6-23e8-4367-b98d-5a23fe5e37e6\", \"artifact\": {\"artifactId\": \"quote\", \"name\": \"quote\", \"parts\": [{\"data\": {\"guests\": 40.0, \"vendor\": \"catering\", \"approved\": false, \"selection\": \"garden\", \"total_cents\": 96000.0, \"currency\": \"USD\"}, \"mediaType\": \"application/json\"}]}, \"lastChunk\": true}}, \"id\": \"SendStreamingMessage\", \"jsonrpc\": \"2.0\"}\r\n\r\ndata: {\"result\": {\"statusUpdate\": {\"taskId\": \"5fa79b82-8f2f-4fbf-b9a2-191a80e1edde\", \"contextId\": \"8b94add6-23e8-4367-b98d-5a23fe5e37e6\", \"status\": {\"state\": \"TASK_STATE_COMPLETED\", \"message\": {\"messageId\": \"56374446-be98-431f-95a3-e35c670ccab4\", \"contextId\": \"8b94add6-23e8-4367-b98d-5a23fe5e37e6\", \"taskId\": \"5fa79b82-8f2f-4fbf-b9a2-191a80e1edde\", \"role\": \"ROLE_AGENT\", \"parts\": [{\"text\": \"Quote ready; no money has been spent.\"}]}}}}, \"id\": \"SendStreamingMessage\", \"jsonrpc\": \"2.0\"}\r\n\r\n"
~~~
