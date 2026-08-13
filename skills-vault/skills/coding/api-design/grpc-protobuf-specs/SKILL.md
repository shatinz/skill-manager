---
id: coding.api-design.grpc-protobuf-specs
name: grpc-protobuf-specs
title: gRPC & Protocol Buffers Microservice Specs
category: coding
subcategory: api-design
version: 1.0.0
tags:
- grpc
- protobuf
- microservices
- rpc
- go
- python
trust_rating: 0.89
estimated_tokens: 1150
description: Define high-performance backward-compatible gRPC service definitions,
  Proto3 contracts, streaming RPCs, and status code propagation across distributed
  services.
trigger_patterns:
- create grpc proto file
- protobuf backward compatibility
- grpc streaming rpc
- microservice proto definition
---

# gRPC & Protocol Buffers Microservice Specs

## Objective
Author clean, forward/backward compatible Proto3 service definitions with field reservation, well-known types, and streaming semantics.

## Best Practices
- Never reuse or reorder field tags. Use `reserved 4, 12 to 15;` when deleting fields.
- Wrap optional primitives in `google.protobuf.StringValue` or Proto3 `optional`.
- Use gRPC rich error model (`google.rpc.Status`) with `ErrorInfo` and `BadRequest` details.
