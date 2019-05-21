from acme.platforms.CommsPlatform import CommsPlatform
from acme.platforms.DisruptorPlatform import DisruptorPlatform
from acme.Environment import Environment
import random
import numpy as np

# Specify parameters
numberOfFrequencyBins = 10  # Number of frequency bins in the environment
maxTxQueue = 30  # Maximum number of packets in queue for each blue agent
numMaxDisruptionTokens = 4  # Maximum number of disruption tokens for red agent
numTimeStepsPerEpoch = 10  # Number of time steps per time epoch
mac = "rr"

# Instantiate communications platforms
plat0 = CommsPlatform("c1", theMaxSize=maxTxQueue)
plat1 = CommsPlatform("c2", theMaxSize=maxTxQueue)
plat2 = CommsPlatform("c3", theMaxSize=maxTxQueue)
allPlatforms = (plat0, plat1, plat2)

# Instantiate disruptor
theDisruptor = (DisruptorPlatform("d1", numMaxDisruptionTokens, numberOfFrequencyBins, numTimeStepsPerEpoch),)

# Define global connectivity/adjacency matrix
adjMatrix = np.full((4,4), False, dtype=bool)
adjMatrix[0,1:3] = True
adjMatrix[1,0] = True
adjMatrix[1,2] = True
adjMatrix[2,0:2] = True
adjMatrix[3,0:3] = True

# Instantiate environment
env = Environment(adjMatrix, allPlatforms, theDisruptor, numberOfFrequencyBins, theMediumAccessMethod=mac, theSlidingWindow=2.0)

# Run simulation
deltaT = 0.25
numSteps = 20
for t in range(numSteps):
    for p in allPlatforms:
        # Determine if data should be added to transmit queue
        doTxData = bool(random.random() > 0.5)
        # Create data to add to transmit queue
        if doTxData:
            # Assign random data payload
            txPayload = random.random()
            # Assign random destination
            destID = random.sample(p.destIDs, 2)
            # Add packet to transmit queue
            p.txData(txPayload, destID)

            # Obtain any received data
            theRxData = p.rxData()
            
    env.step(deltaT)
    
