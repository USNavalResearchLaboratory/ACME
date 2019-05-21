from acme.platforms.CommsPlatform import CommsPlatform
from acme.coordinators.CommsCoordinator import CommsCoordinator
import random
import numpy as np
import unittest

class TestCommsCoordinator ( unittest.TestCase ):

    def setUp ( self ):
        # Instantiate CommsPlatforms
        platform1 = CommsPlatform(0)
        platform2 = CommsPlatform(1)
        allPlatforms = (platform1, platform2)
        platform1.destIDs = [1]
        platform2.destIDs = [0]

        self.platforms = allPlatforms

    
    #FIXME
    @unittest.skip
    def test_roundRobin ( self ):
        """
        Test that ensures Round Robin works correctly
        """
        allPlatforms = self.platforms

        # Instantiate CommsCoordinator
        numFrequencyBins = 2
        coordinator = CommsCoordinator(allPlatforms, numFrequencyBins, "rr")

        # Create and transmit data
        numSteps = 20
        txPayloads = [None] * len(allPlatforms)
        for pIndex, p in enumerate(allPlatforms):
            txPayloads[pIndex] = [random.random() for t in range(numSteps)]
            for t in range(numSteps):
                p.txData(txPayloads[pIndex][t], [(pIndex+1)%len(allPlatforms)])
        
        for t in range(numSteps):
            theData = coordinator.step()
            for binIndex in range(numFrequencyBins):
                self.assertEqual(theData[binIndex].payload, txPayloads[0])


    #TODO
    def test_tdma ( self ):
        """
        Test that ensures TDMA works correctly
        """
        allPlatforms = self.platforms

        # Instantiate CommsCoordinator
        numFrequencyBins = 2
        coordinator = CommsCoordinator(allPlatforms, numFrequencyBins, "tdma")

        
    #TODO
    def test_fdma ( self ):
        """
        Test that ensures FDMA works correctly
        """
        pass

#if __name__ == '__main__':
#    unittest.main()
