# Framework

## Introduction

The structure of the framework is derived from the assumptions of the asynchronous model in MPC. We assume that messages can arrive in any order and with significant delay; the only guarantee is that they will eventually be delivered.  

For this reason, it is necessary to prepare the mailbox to receive any message—even those from a subprotocol that has not yet started locally. In this protocol, which subprotocol will be started is predictable, so it is feasible to prepare the mailbox to receive any possible message and hold it until the subprotocol begins.

## Termination

Asynchronous protocols provide some termination guarantees. While some subprotocols may terminate only under additional conditions (e.g., the dealer is honest), the protocol as a whole will produce a result in finite time, provided resilience is respected (malicious parties ≤ *t* ≤ (N−1)/4).  

However, just because we have reached the result of a protocol or a subprotocol does not mean we can stop participating. Honest parties may still require messages from us to reach their own result.  

The function `stop()` is available for protocols where you can be sure you are no longer needed (e.g., you have already sent all the messages you can). For the protocol as a whole, however, there is a grace period to allow other parties to finish computation before shutting down. This is a mild violation of asynchronous assumptions, but it is necessary in practice we cannot let the protocol run indefinitely.

## Subprotocols

As described in the paper, the purpose of this framework is to build protocols by composition. Each subprotocol is defined as an event-based state machine, handled by the `protocol_manager`, which routes messages to the correct protocol instance and controls execution flow.  

Each instance of a protocol is given an ID, composed of the activation path. Since many protocols invoke multiple instances of the same subprotocol, each step of the path also has an index. For example:

```
/main_0/avss_11/bracha_0/
```

This means that this is the first instance of Bracha’s broadcast protocol, started by the twelfth instance of AVSS, which itself was started by the root protocol `main`. Protocol IDs always end with `/`.

## Messages

Each message consists of an ID, the `party_id` of the sender, the `party_id` of the receiver, and the data. Since communication channels are assumed to be secure, we trust that nobody can forge the `from` field (the router rejects any message with an inconsistent `from`).  

**Message format:**

```json
{
  "messageid": "/main_0/avss_11/acast_0/consistencycheck",
  "from": int,
  "to": int,
  "data": bytes
}
```

When sending a message, the ID is constructed as the protocol instance ID + the message name. When received by the protocol, an additional suffix `_{from}` is appended to distinguish the sending party. Any duplicate message with the same ID from the same party will be discarded (honest parties do not double-send).

## Infrastructure

When started, the `start.sh` script takes in the parameters, writes the corresponding `docker-compose.yml` file, and spins up the router and N parties. These parties then participate in the protocol over the Docker network and shut down when finished. Any information saved using the `log()` utility is available in the `outputs/` directory.
