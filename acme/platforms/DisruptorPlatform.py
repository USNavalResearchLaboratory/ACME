from .Platform import Platform
from ..EmissionObj import DisruptionToken
import random

class DisruptorPlatform(Platform):
    """
    Models a `Disruptor Platform` that can transmit `disruption tokens` 
    to interfere with `Packets` transmitted from `Communications 
    Platforms`.

    Attributes
    ----------
    numMaxTokens : int
        The maximum number of :class:`.DisruptionToken` that may be 
        transmitted per time epoch.
    numFrequencyBins : int
        The number of frequency bins in the :class:`.Environment`.
    numTimeStepsPerEpoch : int
        The number of time steps per time epoch.
    numTokensRemaining : int
        The number of :class:`.DisruptionToken` remaining available to 
        be transmitted in the current time epoch.
    commsDestIDs : list
        The list of identification attributes :attr:`.id` for all 
        :class:`.CommsPlatform` that this platform may interfere with.
    env : list of lists
        This platform's current view and observation of the 
        :class:`.Environment`.
        Has same format as :attr:`.Environment.data`.
    """
    
    def __init__ ( self, theID, theNumMaxTokens=10, theNumFrequencyBins=10, theNumTimeStepsPerEpoch=10, initialPos=[0,0,0], initialVel=[0,0,0], initialAcc=[0,0,0] ):
        """
        Parameters
        ----------
        theID : any
            The identification for this platform.
            May be of any data type (int, str, etc.).
        theNumMaxTokens : int
            The maximum number of :class:`.DisruptionToken` that may 
            be transmitted per time epoch.
        theNumFrequencyBins : int
            The number of frequency bins in the :class:`.Environment`.
        theNumTimeStepsPerEpoch : int
            The number of time steps per time epoch.
        initialPos : list of float
            The initial position of the platform in cartesian coordinates.
            List has length 3 and is specified as :math:`[p_x,p_y,p_z]`.
        initialVel : list of float
            The initial velocity of the platform in cartesian coordinates.
            List has length 3 and is specified as :math:`[v_x,v_y,v_z]`.
        initialAcc : list of float
            The initial acceleration of the platform in cartesian coordinates.
            List has length 3 and is specified as :math:`[a_x,a_y,a_z]`.
        """

        super().__init__( theID, initialPos, initialVel, initialAcc )
        # theID is currently not used by ACME for DisruptorPlatforms

        # Specify the maximum number of disruptor tokens
        if theNumMaxTokens < 0 or type(theNumMaxTokens) is not int:
            raise ValueError("Number of disruption tokens must be non-negative integer.")
        self.numMaxTokens = theNumMaxTokens
        # Specify the number of discrete frequency bins in the environment
        if theNumFrequencyBins < 1 or type(theNumFrequencyBins) is not int:
            raise ValueError("Number of frequency bins must be an integer greater than zero.")
        self.numFrequencyBins = theNumFrequencyBins
        # Specify the number of time steps per time epoch
        if theNumTimeStepsPerEpoch < 1 or type(theNumTimeStepsPerEpoch) is not int:
            raise ValueError("Number of time steps per epoch must be an integer greater than zero.")
        self.numTimeStepsPerEpoch = theNumTimeStepsPerEpoch

        # Initialize number of disruption tokens left in current time epoch
        self.numTokensRemaining = theNumMaxTokens

        # Initialize array of destination IDs
        self.commsDestIDs = []
        
        # Initialize current observation of Environment
        # Will be directly updated by Environment, and will be a list of [[CommsCoordinator data], [[Disruptor1 data], [Disruptor2 data], ...]]
        self.env = None

    @property
    # Specify array of destination IDs that this object can transmit to
    def commsDestIDs(self):
        return self.__commsDestIDs
    @commsDestIDs.setter
    def commsDestIDs(self, value):
        if type(value) is not list:
            raise ValueError("Node IDs must be specified as a list of values.")
        self.__commsDestIDs = value
    
    def step ( self, deltaT ):
        """
        Advance the platform's position, velocity, and acceleration by 
        ``deltaT`` seconds.
        Reset the number of `disruption tokens` available if a new 
        time epoch has been reached.
        
        Parameters
        ----------
        deltaT : float
            The number of seconds to advance the platform by.
        """

        super().step(deltaT)

        # Determine if a new time epoch has begun
        if self.elapsedTimeSteps % self.numTimeStepsPerEpoch == 0:
            # Reset the number of disruption tokens
            self.numTokensRemaining = self.numMaxTokens
        

    def getDisruptions ( self ):
        """
        Decide which `disruption tokens` should be placed in which 
        frequency bins for the current time step.

        Returns
        -------
        tokens : list
            List indicating which `disruption tokens` have been placed 
            in which frequency bins.
            Each element of the list is either ``None`` or contains a 
            single :class:`.DisruptionToken`.
            List has length :attr:`numFrequencyBins`.
        
        Todo
        ----
        Develop more methods for allocating `disruption tokens` other 
        than random placement into frequency bins.
        """

        # Get disruption tokens for all frequency bins
        
        # Obtain number of tokens to use during this time step,
        #     given constraint of total number of tokens available for entire time epoch
        # TODO: Need to leverage self.env
        numTokensToUse = min(self.numTokensRemaining, 1)  #FIXME
        
        # Initialize disruption tokens
        tokens = [None] * self.numFrequencyBins

        # Ensure number of disruption tokens is not greater than number of frequency bins
        if numTokensToUse > self.numFrequencyBins:
            numTokensToUse = self.numFrequencyBins
        
        assert (numTokensToUse <= self.numTokensRemaining), "Number of tokens requested to use is greater than number of tokens available!"

        self.numTokensRemaining -= numTokensToUse

        # Assign tokens to frequency bins
        index = random.sample(range(self.numFrequencyBins), numTokensToUse)
        for i in index:
            tokens[i] = DisruptionToken(self.id, self.commsDestIDs, self.elapsedTime)
            tokens[i].freqBin = i
            tokens[i].position = self.pos
        return tokens
