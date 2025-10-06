# Protocols

## Bracha

This protocol is cited in the paper:  
[14] Bracha, G.: *Asynchronous Byzantine Agreement Protocols*. Inf. Comput. 75(2), 130–143 (1987)

Bracha’s protocol is used to broadcast a message from one party to all others. It provides the following guarantees:

- If the sender is honest, the protocol will terminate.  
- If one honest party terminates with a value, then all honest parties will terminate with the same value.  

### Protocol Steps

1. **INIT phase**  
   The designated sender broadcasts an `INIT` message with the chosen value to all other parties.

2. **ECHO phase**  
   Upon receiving an `INIT` message, a party sends an `ECHO` message with that value to all other parties.

3. **READY trigger**  
   - If a party receives **N−t** `ECHO` messages with the same value, **or**  
   - If it receives **t+1** `READY` messages with the same value,  

   then it sends a `READY` message with that value to all other parties.

4. **Termination condition**  
   Once a party receives **2t+1** `READY` messages with the same value, it decides on that value and terminates.  

   If it has already broadcast a `READY`, there is nothing further to do, and the protocol can safely stop.
