from acme.platforms.CommsPlatform import CommsPlatform
from acme.platforms.DisruptorPlatform import DisruptorPlatform
from acme.Environment import Environment
import random
import numpy as np
import queue
import copy
import unittest

class TestEnvironment ( unittest.TestCase ):

    def test_dataTransfer ( self ):
        """
        Test that ensures data transferred by one CommsPlatform is received by the intended Comms Platforms
        """
        # Instantiate CommsPlatforms
        platform1 = CommsPlatform(1)
        platform2 = CommsPlatform(2)
        platform3 = CommsPlatform(3)
        allPlatforms = (platform1, platform2, platform3)
        rxPlatforms = [platform2, platform3]
        nonRxPlatforms = [platform1]

        # Define connectivity/adjacency matrix
        adjMatrix = np.full((3,3), True, dtype=bool)
        
        # Instantiate Environment
        env = Environment(adjMatrix, allPlatforms)

        # Create and transmit data
        numSteps = 20
        txPayloads = [random.random() for i in range(numSteps)]
        
        # Run simulation
        deltaT = 0.25
        for t in range(numSteps):
            platform1.txData(txPayloads[t], [2,3])
        
            # Ensure platforms receive correct data
            for p in rxPlatforms:
                # Obtain any received data
                theRxData = p.rxData()

                if t == 0:
                    self.assertEqual(theRxData, None)
                else:
                    self.assertEqual(theRxData, txPayloads[t-1])
            
            # Ensure platforms that are not supposed to receive any data in fact have not
            for p in nonRxPlatforms:
                # Obtain any received data
                theRxData = p.rxData()
                self.assertEqual(theRxData, None)

            # Step simulation
            env.step(deltaT)


    def test_delay ( self ):
        """
        Test that ensures Disruptor Platform awareness of the Environment is delayed correctly
        """
        # Instantiate CommsPlatforms
        platform1 = CommsPlatform(1)
        platform2 = CommsPlatform(2)
        platform3 = CommsPlatform(3)
        allPlatforms = (platform1, platform2, platform3)
        
        # Instantiate DisruptorPlatform
        disruptor = DisruptorPlatform(1, 0)
        
        # Define connectivity/adjacency matrix
        adjMatrix = np.full((4,4), True, dtype=bool)
        
        # Instantiate Environment
        delay = 2
        env = Environment(adjMatrix, allPlatforms, (disruptor,), theDisruptorDelay=delay)

        # Create and transmit data
        numSteps = 20
        txPayloads = [random.random() for i in range(numSteps)]
        
        # Run simulation
        deltaT = 0.25
        envQueue = queue.Queue()
        for t in range(numSteps):
            platform1.txData(txPayloads[t], [2])

            envQueue.put(copy.deepcopy(env.data))
            
            # Compare current value from Environment with delayed value from Disruptor
            if t >= delay:
                pastEnv = envQueue.get()
                for platformIndex in range(len(env.data)):
                    for binIndex in range(env.numFrequencyBins):
                        if pastEnv[platformIndex][binIndex]:
                            self.assertEqual(pastEnv[platformIndex][binIndex].sourceID, disruptor.env[platformIndex][binIndex].sourceID)
                            self.assertEqual(pastEnv[platformIndex][binIndex].destID, disruptor.env[platformIndex][binIndex].destID)
                            self.assertEqual(pastEnv[platformIndex][binIndex].payload, disruptor.env[platformIndex][binIndex].payload)
                            self.assertEqual(pastEnv[platformIndex][binIndex].msgID, disruptor.env[platformIndex][binIndex].msgID)
                            self.assertEqual(pastEnv[platformIndex][binIndex].freqBin, disruptor.env[platformIndex][binIndex].freqBin)
                            #self.assertEqual(pastEnv[platformIndex][binIndex].position, disruptor.env[platformIndex][binIndex].position)
                        else:
                            self.assertEqual(pastEnv[platformIndex][binIndex], disruptor.env[platformIndex][binIndex])

            # Step simulation
            env.step(deltaT)


    def test_time ( self ):
        """
        Test that ensures that emissions have the correct time of creation
        """
        # Instantiate CommsPlatform
        platform1 = CommsPlatform(1)
        platform2 = CommsPlatform(2)
        allPlatforms = (platform1, platform2)
        
        # Instantiate DisruptorPlatform
        disruptor = DisruptorPlatform(1, 0)
        
        # Define connectivity/adjacency matrix
        adjMatrix = np.full((3,3), True, dtype=bool)
        
        # Instantiate Environment
        env = Environment(adjMatrix, allPlatforms, (disruptor,))

        # Create and transmit data
        numSteps = 20
        txPayloads = [random.random() for i in range(numSteps)]
        
        # Run simulation
        deltaT = 0.25
        for t in range(numSteps):
            platform1.txData(txPayloads[t], [2])
            # Verify emission time is correct
            if t > env.disruptorDelay:
                self.assertEqual(disruptor.env[0][0].time, deltaT * (t-env.disruptorDelay-1))
            
            # Step simulation
            env.step(deltaT)


#if __name__ == '__main__':
#    unittest.main()
