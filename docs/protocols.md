# Protocols

## Bracha

This protocol is cited in the paper:  
[14] Bracha, G.: *Asynchronous Byzantine Agreement Protocols*. Inf. Comput. 75(2), 130–143 (1987)

Bracha’s protocol is used to broadcast a message from one party to all others. It provides the following guarantees:

- If the sender is honest, the protocol will terminate.  
- If one honest party terminates with a value, then all honest parties will terminate with the same value.  

### Parameters

The protocol takes one optional static parameter:
   - "speaker" : who the speaker is, can be omitted if unknown at compile time
and one mandatory static parameter:
   - "content\_schema" : the schema to validate the structure of the content (see schemas)
The protocol always takes one parameter "speaker" at runtime, for the speaker only it also takes a "value" parameter

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


## PackedVSS

This protocol is described in chapter 4 of the paper

It also includes the batching optimization from chapter 7 to bring the cost of each secret linear in the number of parties

The protocol provides a way to share multiple secrets simultaneasly in a way that is verifiable, meaning that it satisfay:

- Validity: If the dealer is honest, then the protocol must terminate. At the end of the reconstruction phase, all honest parties must output S
- Secrecy: The view of the adversary in the sharing phase is independent of S
- Binding: The view of the honest parties at the end of the sharing phase uniquely define some secret S' and reconstruction of S' is guaranteed

the protocol uses Bracha's protocol as a primitive for reliable broadcast

### Parameters

The protocol takes two mandatory static parameters:
   - "dealer" : the party id of the dealer
   - "batching" : the number of polynomials batched in a single sharing
they must also be provided at runtime, the speaker must also provide at runtime:
   - "input" : a list of BivariatePolynomials of degree t+t//2 in x and t in y

### Protocol Steps

1. **Dealing shares**
   The dealer extracts from the input bivariate polynomial, two univariate polynomials for each party, one in x amd one in y, by fixing the other value to its party id, and sends them to that party

2. **Pairwise consistency checks**
   Upon receiving the share from the dealer, the party verifies that they are two univariate polynomials in degrees t and t+t//2, then sends to each party an exchange message with the evaluation of their shares at the party id of other
   When receiving an exchange message, it checks that these evaluations match, and if so broadcast GOOD

3. **Finding a star**
   When two parties broadcast GOOD about each other we take note of that and build a graph with these edges, the dealer tries to find a CD star in this graph and if it does it broadcasts CDGF
   Other parties when receiving the CDGF star verify it, and if fails, they wait for more edges to arrive

4. **Reconstruction**
   Once verified the star, if the party belongs to G it means that his shares of g(y) are correct, otherwise it uses reed solomon decoding with the points received in the exchanges to find a consistent polynomial g(y), then redo the exchange with the new function caling it reconstruct and sends it to all those not in F, if the solution is not unique waits for more points
   If the parties doesn't belong to F, it also uses reed solomon decoding to find f(x), using both the points from exchanges and points from reconstruct messages

5. **Termination**
   Once found valid f(x) ang g(y) we can safely exit the protocol

*this is done with multiple instances at once, as defined by the parameter "batching" the GOOD and star finding parts are done once for all the instances togheter*

