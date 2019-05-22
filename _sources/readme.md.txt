# Introduction and Description
This repository contains the abstracted communications modelling environment (ACME), which is a library of classes and methods for simulating communications networks and potential sources of interference.

Within this model, time and frequency are divided into discrete steps and bins, respectively.  Information or data is treated as discrete units.


## Entities
The model contains four entity types (i.e., platform types):

### Communications agent
This entity generates units of information, and then places the information units into its own queue for transmission.  If the transmit queue is full, then any newly generated units are discarded.
Additionally, this entity receives units of information intended for itself, and then places the information units into its own receive queue.  Similarly to the transmit queue, if the receive queue if full, then any newly received units are discarded.

At each time step, this entity's primary action is to decide which unit of information from its transmission queue (if any) to present to the [Communications Coordinator](#communications-coordinator).  Additionally, at each time step, this entity may process any information units (if any) from its receive queue.

### Communications coordinator
This entity implements a policy of mapping information units presented by one or multiple [Communications Agents](#communications-agent) to the [Environment](#environment).
This entity essentially models and represents the MAC protocols of the communications protocol stack.

At each time step, this entity's primary action is to select a subset of Communications Agents which have units of information to transmit by having non-empty transmit queues, take their units of information, and place their units of information into the Environment for delivery to their intended destinations.

### Environment
This entity implements an abstracted physical layer model.
This entity contains a fixed number of frequency bins, and each frequency bin may potentially contain one unit of information.

At each time step, this entity's primary action is to update the contents of frequency bins with units of information presented by the Communications Coordinator.
Then, the entity passes and delivers the units of information to their intended recipients.

### Interference source (Disruptors)
This entity has the ability to disrupt units of information and prevent them from being delivered to their intended recipients.
This is accomplished by selecting the specific frequency bins within the Environment and times during which interference occurs. Interference is indicated by Disruption Tokens placed into the corresponding frequency bin.  Each interference source also has a configurable number of Disruption Tokens, meant to represent a finite resource (e.g., energy). ACME currently supports only random placement of Disruption Tokens. Alternative methods for subjecting the Environment to interference is at the discretion of the user.


## Constraints
* Communications Agents can only offer one unit of information per time step. However, this single unit of information has no further limitation, and may consist of any amount of data of any type.
* The Communications Coordinator must dispose of all units of information that it selects from Communications Agents. This means that the Communications Coordinator cannot accept any information units from Communications Agents that it cannot fit into the frequency bin space of the Environment.  In other words, the Communications Coordinator does not have its own internal buffer or queue for information units.
* Communications Agents must drop information units that coincide in time and frequency with Disruption Tokens.
* Time is divided into both steps and epochs, such that a time epoch contains a fixed integer number of time steps. At the beginning of each time epoch, the number of available Disruption Tokens resets.


## Objectives
### Communications agent
* Maximize the delivery of its own information units (units per time)
### Communications coordinator
* Maximize the delivery of all information units throughout the network
### Environment
* Faithfully pass and deliver information units and Disruption Tokens to correct recipients at each time step
### Interference source
* Disrupt information units in frequency bins


## Notes and Comments
This is a simulation of different objectives by different entities. In principle, this could be simulated without any dialogue among them. Alternatively, if Communications Agents were able to talk with one another and/or with the Communications Coordinator (via an out-of-band mechanism), then different (and equally interesting) dynamics might arise.

These entity models are deliberately configured to be extensible, by revisiting the assumptions below.


## Assumptions
The following simplifying assumptions have been made within this model:

* Flat Earth model (platform positions are represented in cartesian coordinates).
* The network topology may be changed by the user between any time step.
* The Environment does not drop information units (i.e., they are perfectly delivered if the Agents are connected via the network topology). This can be reconsidered in later iterations.
* If Interference Sources were capable of agency and responding to the Environment, they would have perfect information about the Environment albeit with at least one time step of delay. 
* Communications Coordinator is not able to directly observe Disruption Tokens but may infer their presence through the inability to transmit data through the Environment.
* Communications Platforms listen to all frequency bins in the Environment.


## Example usage
An example script has been developed that demonstrates the primary capabilities of these models.  The entry point into this main program is run by executing:

```
python3 ./runModel.py
```

This model has been tested to run successfully using Python 3.4.9 and 3.6.6.


## Unit tests
This module contains a collection of unit tests in the `tests` directory.  All unit tests are run by executing:

```
python3 -m unittest discover -s ./tests
```


## Todo -- Future development
* Implement propagation and/or processing delay.  Currently, all Communications Agents receive their intended information units after 1 time step, regardless of platform positions.  Likewise, all Interference Sources observe the status of the Environment after a delay of a fixed number of time steps, regardless of platform positions.
* Implement a routing capability for Communications Agents (i.e., the ability to transmit information units via relaying through another Communications Agent).  Currently, all network topology links are only point-to-point.
  * The implementation for Communications Agents could be changed to maintain two separate transmit queues (i.e., one for its own information units and one for relay).
  * Leveraging a routing protocol, a route discovery process for Communications Agents may be developed.
* Define an appropriate metric of performance for Communications Agents and Communications Coordinator (e.g., average of negative log of the per source throughput).
* Develop more sophisticated schemes for the Communications Coordinator.  Simple ones like TDMA and FDMA are currently implemented.  Future development could introduce more advanced coordination schemes including adaptation, planning, and even cognitive processing.
* Develop more sophisticated schemes for Disruption Token allocation by Interference Sources.  Currently, only random allocation is implemented.
