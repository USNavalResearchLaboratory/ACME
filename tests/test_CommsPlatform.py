from acme.platforms.CommsPlatform import CommsPlatform
from acme.Environment import Environment
import numpy as np
import unittest

class TestCommsPlatform ( unittest.TestCase ):

    def test_uniqueID ( self ):
        """
        Test that ensures all CommsPlatforms have unique IDs
        """
        # Instantiate CommsPlatforms
        theID = 0
        platform1 = CommsPlatform(theID)
        platform2 = CommsPlatform(theID)
        allPlatforms = (platform1, platform2)

        # Define connectivity/adjacency matrix
        adjMatrix = np.full((2,2), True, dtype=bool)
        
        # Instantiate Environment
        self.assertRaises(AssertionError, Environment, adjMatrix, allPlatforms)
        #env = Environment(adjMatrix, allPlatforms)


    @unittest.expectedFailure
    def test_validDestID ( self ):
        """
        Test that ensures destination ID for packet must be in connectivity list
        """
        # Instantiate CommsPlatforms
        theID = 0
        platform = CommsPlatform(theID)

        # Define connectivity/adjacency matrix
        adjMatrix = np.full((1,1), True, dtype=bool)

        # Instantiate Environment
        env = Environment(adjMatrix, (platform,))

        # Transmit data
        thePayload = 1
        # Should produce no error
        platform.txData(thePayload, [theID])
        # Should produce error
        self.assertRaises(AssertionError, platform.txData, thePayload, [theID+1])


#if __name__ == '__main__':
#    unittest.main()
