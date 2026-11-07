# Glossary

## A2A

Agent2Agent: a shared protocol for independently operated agents to exchange work.

## Agent

A program that can perform work or decide how to pursue a request.

## Client

The side that initiates a protocol operation.

## Server

The side that accepts requests and returns results.

## Agent Card

A machine-readable description of an agent's identity, interfaces, skills and security.

## Discovery

Finding and reading an agent's card before choosing how to contact it.

## Registry

A directory of agent locations; membership alone does not establish trust.

## Skill

A named, documented capability offered by an agent.

## Capability

A declared protocol feature such as streaming or push notifications.

## Interface

An endpoint combined with its binding, protocol version and optional tenant.

## Message

One communication containing a role, identifier and parts.

## Message ID

An identifier assigned by a message's creator, distinct from a request or task ID.

## Part

One content item: text, raw bytes, URL or structured JSON value.

## Artifact

A named deliverable produced by a task.

## Task

Tracked work with an identifier, state, optional history and artifacts.

## Task ID

The server-assigned identifier used to inspect, continue or cancel work.

## Context ID

A server-scoped grouping of related interactions, analogous to a project folder.

## Submitted

The task has been acknowledged.

## Working

The agent is processing the task.

## Input-required

Work is interrupted until the client supplies information.

## Auth-required

Work is interrupted until external authorization requirements are satisfied.

## Completed

The task finished successfully and cannot be restarted.

## Failed

The task finished unsuccessfully because execution failed.

## Rejected

The agent declined to perform the work.

## Canceled

The task stopped before normal completion following cancellation.

## Terminal state

A state from which the same task does not resume.

## Interrupted state

A paused state from which the task may continue.

## HTTP

A request/response web protocol with methods, headers, status codes and a body.

## HTTPS

HTTP protected by TLS encryption and peer authentication.

## URL

A location identifying a resource and how to access it.

## URI

An identifier that may identify a resource without providing a fetchable location.

## Endpoint

An address accepting a particular kind of request.

## Header

Transport metadata such as authorization or a content type.

## Body

The content carried by an HTTP request or response.

## Status code

A transport result such as 200 success, 401 unauthenticated or 404 not found.

## JSON

A text representation of objects, arrays, strings, numbers, booleans and null.

## JSON-RPC

A remote procedure call envelope containing a method, parameters and correlation ID.

## gRPC

A remote procedure call system commonly using protobuf over HTTP/2.

## Protobuf

A schema language and binary serialization system.

## ProtoJSON

The defined JSON representation of protobuf messages, including field and enum names.

## Binding

A mapping of abstract protocol operations onto a concrete transport.

## SSE

Server-Sent Events: named or data events sent through a long-lived HTTP response.

## Streaming

Receiving progress or partial output before the work is finished.

## Polling

Repeatedly asking for the current state.

## Webhook

An HTTP callback initiated by a remote service.

## Push notification

An asynchronous update delivered to a configured receiver.

## Chunk

One portion of an artifact delivered incrementally.

## Append

An instruction to add content to an existing artifact with the same identifier.

## Last chunk

The final portion of one artifact; it does not by itself finish the task.

## Authentication

Checking who a caller or service is.

## Authorization

Checking what an authenticated identity may do.

## Bearer token

A credential whose holder can present it for access.

## API key

A service credential provisioned outside the protocol.

## OAuth

A framework for obtaining delegated access to protected resources.

## OpenID Connect

An identity layer and discovery conventions built on OAuth.

## JWT

A compact claims format that must be verified before its claims are trusted.

## JWS

A standard for signing a payload and associated protected headers.

## JWKS

A JSON set of public keys, which must itself come from a trusted source.

## JCS

JSON canonicalization: a deterministic byte representation for signing.

## TLS

Transport Layer Security: encryption and peer authentication for a connection.

## mTLS

TLS that also authenticates the client using a certificate.

## PKCE

A proof mechanism that helps protect OAuth authorization codes from interception.

## Scope

A named permission associated with a credential.

## Tenant

An application routing or isolation partition; a request field is not authorization.

## SSRF

Server-side request forgery: inducing a server to contact an unintended destination.

## DNS rebinding

Changing a hostname's resolved address between validation and connection.

## Replay attack

Reusing a previously valid message to trigger processing again.

## Nonce

A value intended to be used once, useful when detecting replay.

## HMAC

A message authentication code using a shared secret.

## Prompt injection

Untrusted content attempting to act as instructions to a model or agent.

## Confused deputy

A more privileged service being tricked into using its authority for someone else.

## Allow-list

An explicit set of destinations or actions the application permits.

## LLM

A language model that predicts output from supplied context.

## Tool calling

A model requesting application code to invoke a named function with arguments.

## MCP

Model Context Protocol: connecting a host to tools and resources.

## Async

Cooperative execution that yields while awaiting work.

## ASGI

A Python interface between asynchronous web applications and their servers.

## Coroutine

An asynchronous function's resumable computation.

## Timeout

A bound on waiting; it does not prove remote work was undone.

## Retry

A new attempt after a failure or uncertain result.

## Idempotency

An application property that repeated requests do not repeat a side effect.

## Compensation

A new business action that offsets an earlier successful action.

## Trace

Related operation records showing work across components.

## Span

One timed operation inside a trace.

## Trace context

Transported identifiers connecting spans across services.

## Conformance

Agreement with specified protocol requirements.

## TCK

Technology Compatibility Kit: the project's official compatibility tests.

## Evaluation

Checking whether a result satisfies business requirements.

## Golden scenario

A fixed input with expected delegations, states and deliverables.

## Extension

An identified addition to a protocol contract, declared and activated explicitly.

## Pagination

Returning a bounded portion of a collection with a token for the next portion.

## Persistent store

Storage that survives a process restart.

## Replica

Another running copy of a service.

## Load balancer

A component that distributes requests across service copies.

## Container

A packaged process environment; it is not by itself a security or scaling strategy.

## ADR

Architecture decision record: context, alternatives, decision and consequences.
