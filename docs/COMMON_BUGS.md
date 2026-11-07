# Common bugs

Each entry links to a repair task. Inputs and incorrect outputs come from the supplied runnable starter.

## 1. Select the loopback vendor URL

**Symptom:** input {'port': 8100} returns 'http://0.0.0.0:8100'; expected 'http://127.0.0.1:8100'.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Bind local teaching services to the loopback interface.

[Repair 00-02](../gym/tasks/00/00-02_fix/task.md)

## 2. Construct a SendMessage envelope

**Symptom:** input {'id': 1, 'message': {'messageId': 'm1', 'role': 'ROLE_USER', 'parts': [{'text': 'Quote a venue'}]}} returns {'jsonrpc': '2.0', 'id': 1, 'method': 'SendMessage', 'params': {'messageId': 'm1', 'role': 'ROLE_USER', 'parts': [{'text': 'Quote a venue'}]}}; expected {'jsonrpc': '2.0', 'id': 1, 'method': 'SendMessage', 'params': {'message': {'messageId': 'm1', 'role': 'ROLE_USER', 'parts': [{'text': 'Quote a venue'}]}}}.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** The method parameters contain a message object, not its individual fields.

[Repair 01-02](../gym/tasks/01/01-02_fix/task.md)

## 3. Select a compatible advertised interface

**Symptom:** input {'interfaces': [{'url': 'http://print', 'protocolBinding': 'GRPC', 'protocolVersion': '1.0'}, {'url': 'http://venues', 'protocolBinding': 'JSONRPC', 'protocolVersion': '1.0'}], 'supported': ['JSONRPC']} returns 'http://print'; expected 'http://venues'.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Respect both protocol version and binding, preserving advertised preference.

[Repair 02-02](../gym/tasks/02/02-02_fix/task.md)

## 4. Order a task lifecycle stream

**Symptom:** input {'artifacts': ['quote']} returns ['working', 'quote', 'task']; expected ['task', 'working', 'quote', 'completed'].

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Introduce the task before updates and explicitly reach a final state.

[Repair 03-02](../gym/tasks/03/03-02_fix/task.md)

## 5. Classify a response payload

**Symptom:** input {'message': {'messageId': 'm1'}} returns 'task'; expected 'message'.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Inspect the response wrapper instead of assuming every reply creates a task.

[Repair 04-02](../gym/tasks/04/04-02_fix/task.md)

## 6. Distinguish terminal from interrupted states

**Symptom:** input {'state': 'TASK_STATE_INPUT_REQUIRED'} returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Input-required and auth-required are resumable; terminal states are not.

[Repair 05-02](../gym/tasks/05/05-02_fix/task.md)

## 7. Preserve binary files using ProtoJSON

**Symptom:** input {'text': 'floor plan', 'media_type': 'text/plain', 'filename': 'plan.txt'} returns {'raw': 'floor plan', 'mediaType': 'text/plain'}; expected {'raw': 'Zmxvb3IgcGxhbg==', 'mediaType': 'text/plain', 'filename': 'plan.txt'}.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Binary content becomes base64 in JSON; keep the media type and filename.

[Repair 06-02](../gym/tasks/06/06-02_fix/task.md)

## 8. Assemble artifact chunks by artifact ID

**Symptom:** input [{'id': 'a', 'text': 'Mic '}, {'id': 'b', 'text': 'Light'}, {'id': 'a', 'text': 'check', 'append': True}] returns {'a': 'check', 'b': 'Light'}; expected {'a': 'Mic check', 'b': 'Light'}.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Append only to an existing artifact with the same ID.

[Repair 07-02](../gym/tasks/07/07-02_fix/task.md)

## 9. Map core operations to HTTP routes

**Symptom:** input {'operation': 'GetTask', 'id': 'quote-2'} returns ['POST', '/message:send']; expected ['GET', '/tasks/quote-2'].

**Cause:** the broken transformation omits a required contract condition.

**Fix:** HTTP routes differ from JSON-RPC method strings; protobuf annotations define the mapping.

[Repair 08-02](../gym/tasks/08/08-02_fix/task.md)

## 10. Validate model-selected tool names

**Symptom:** input {'tool': 'send_credentials'} returns 'send_credentials'; expected 'reject'.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** A model suggests tools; application code owns the allow-list.

[Repair 09-02](../gym/tasks/09/09-02_fix/task.md)

## 11. Minimize delegated event data

**Symptom:** input {'guests': 40, 'date': '2027-06-01', 'authorization': 'secret'} returns {'guests': 40, 'date': '2027-06-01', 'authorization': 'secret'}; expected {'guests': 40, 'date': '2027-06-01'}.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Pass only the business fields required by the selected vendor.

[Repair 10-02](../gym/tasks/10/10-02_fix/task.md)

## 12. Normalize framework output at the A2A boundary

**Symptom:** input {'vendor': 'catering', 'amount': '96000'} returns {'vendor': 'catering', 'total_cents': '96000', 'approved': True}; expected {'vendor': 'catering', 'total_cents': 96000, 'currency': 'USD', 'approved': False}.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Map validated framework results into a stable quote contract; never infer spending approval.

[Repair 11-02](../gym/tasks/11/11-02_fix/task.md)

## 13. Choose inventory tools versus remote work

**Symptom:** input {'operation': 'inventory_lookup'} returns 'A2A'; expected 'MCP'.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Internal inventory lookup is a tool; independently owned work remains an agent task.

[Repair 12-02](../gym/tasks/12/12-02_fix/task.md)

## 14. Authorize the requested partner skill

**Symptom:** input {'authenticated': True, 'skill': 'travel.partner_quote', 'scopes': []} returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Authentication alone does not grant partner pricing.

[Repair 13-02](../gym/tasks/13/13-02_fix/task.md)

## 15. Keep task owners isolated

**Symptom:** input {'task': {'owner': 'alice', 'tenant': 'maplewood'}, 'principal': {'subject': 'bob', 'tenant': 'maplewood'}} returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** A matching tenant is not permission to read another caller's task.

[Repair 14-02](../gym/tasks/14/14-02_fix/task.md)

## 16. Reject private and reserved IP addresses

**Symptom:** input {'address': '10.1.2.3'} returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** This IP check is one layer; production fetches also need allow-lists, no redirects and DNS rebinding protection.

[Repair 15-02](../gym/tasks/15/15-02_fix/task.md)

## 17. Detect invalid mixed event streams

**Symptom:** input ['message', 'task'] returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** A direct message is a complete response; a task stream needs a valid introduction and stop condition.

[Repair 16-02](../gym/tasks/16/16-02_fix/task.md)

## 18. Evaluate golden delegations without prose scoring

**Symptom:** input {'actual': ['venues', 'venues'], 'expected': ['venues', 'catering']} returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Match identity and cardinality; equal list lengths do not prove correct delegation.

[Repair 17-02](../gym/tasks/17/17-02_fix/task.md)

## 19. Check required extension activation

**Symptom:** input {'extensions': [{'uri': 'urn:quote:v1', 'required': True}], 'requested': []} returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** A required extension must be understood and requested; optional extensions need not be active.

[Repair 18-02](../gym/tasks/18/18-02_fix/task.md)

## 20. Bound webhook retry attempts

**Symptom:** input {'base_seconds': 1, 'attempt': 2, 'cap_seconds': 3, 'max_attempts': 5} returns 4; expected 3.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Cap both delay and attempts; persist retry state if delivery must survive a restart.

[Repair 19-02](../gym/tasks/19/19-02_fix/task.md)

## 21. Compensate only confirmed holds

**Symptom:** input {'failed': True, 'holds': [{'id': 'hotel', 'confirmed': True}, {'id': 'venue', 'confirmed': False}]} returns ['release:hotel', 'release:venue']; expected ['release:hotel'].

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Compensation is an explicit business action, normally reversing successfully completed steps.

[Repair 20-02](../gym/tasks/20/20-02_fix/task.md)

## 22. Compare cross-language quote semantics

**Symptom:** input {'python': {'total_cents': 100, 'currency': 'USD'}, 'typescript': {'total_cents': 100, 'currency': 'EUR'}} returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Compare semantic values, not generated identifiers or object implementations.

[Repair B1-02](../gym/tasks/B1/B1-02_fix/task.md)

## 23. Select SDK releases by protocol support

**Symptom:** input [{'language': 'Go', 'protocols': ['1.0'], 'stable': True}, {'language': 'Java', 'protocols': ['0.3'], 'stable': True}] returns ['Go', 'Java']; expected ['Go'].

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Official project membership and stable support for the target protocol are separate checks.

[Repair B2-02](../gym/tasks/B2/B2-02_fix/task.md)

## 24. Validate Part oneof content

**Symptom:** input {'text': 'quote', 'data': {}} returns True; expected False.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** A protobuf oneof permits exactly one selected content alternative.

[Repair B3-02](../gym/tasks/B3/B3-02_fix/task.md)

## 25. Follow task pagination tokens

**Symptom:** input {'nextPageToken': 'opaque-2'} returns None; expected 'opaque-2'.

**Cause:** the broken transformation omits a required contract condition.

**Fix:** Use nextPageToken as the next request's pageToken; treat the token as opaque.

[Repair B4-02](../gym/tasks/B4/B4-02_fix/task.md)
