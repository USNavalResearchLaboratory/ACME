from .coordinators.CommsCoordinator import CommsCoordinator
from .platforms.CommsPlatform import CommsPlatform
from .platforms.DisruptorPlatform import DisruptorPlatform
import queue
import numpy as np

class Environment:
    """
    Implements the physical layer propagation model.
    
    Creates an RF communications environment whose frequency space is 
    divided into bins, and time is divided into steps and epochs.
    Ensures all `Communications and Disruptor Platforms` and 
    `Communications Coordinators` are in lock-step and updated 
    appropriately.

    Attributes
    ----------
    commsPlatforms : tuple of :class:`.CommsPlatform`
        The tuple of `Communications Platforms`.
    commsPlatformIDs : tuple
        The tuple containing the identification attribute :attr:`.id` 
        for all platforms in :attr:`commsPlatforms`.
    numCommsPlatforms : int
        The number of `Communication Platforms` (i.e., length of :attr:`commsPlatforms`).
    disruptorPlatforms : tuple of :class:`.DisruptorPlatform`
        The tuple of `Disruptor Platforms`.
    disruptorPlatformIDs : tuple
        The tuple containing the identification attribute :attr:`.id` 
        for all platforms in :attr:`disruptorPlatforms`.
    numDisruptorPlatforms : int
        The number of `Disruptor Platforms` (i.e., length of :attr:`disruptorPlatforms`).
    numFrequencyBins : int
        The number of frequency bins.
    disruptorDelay : int
        The number of time steps behind the current time step which 
        `Disruptor Platforms` observe the status of the `Environment`.
    coordinator : list of :class:`.CommsCoordinator`
        The list of `Communications Coordinators`.
    elapsedTime : float
        The number of simulated seconds that have passed since the 
        simulation began.
    data : list of lists
        The current status of the frequency bins.
        The outer list has length ``len(``:attr:`coordinator` ``) + len(``:attr:`disruptorPlatforms` ``)``.
        Each outer list contains an inner list of length :attr:`numFrequencyBins`.
        Each element of each inner list will contain an :class:`.EmissionObj` or ``None``.
    adjMatrix : numpy.ndarray
        The adjacency matrix denoting one-way active links among 
        `Communications and Disruptor Platforms`.  This matrix is square 
        (but not necessarily symmetric), 
        with each element of the matrix being ``True`` or ``False``.
        Each dimension of the matrix is (:attr:`numCommsPlatforms` + :attr:`numDisruptorPlatforms`).
        If element :math:`(m,n)` in the matrix is ``True``, then:

        =========================== =========================== =======================================================
                            Platform Type                       Description
        ------------------------------------------------------- -------------------------------------------------------
        :math:`m`                   :math:`n`
        =========================== =========================== =======================================================
        :class:`.CommsPlatform`     :class:`.CommsPlatform`     :math:`m` can transmit to :math:`n`
        :class:`.CommsPlatform`     :class:`.DisruptorPlatform` :math:`n` can observe transmissions of :math:`m`
        :class:`.DisruptorPlatform` :class:`.CommsPlatform`     :math:`m` can interfere with :math:`n`
        :class:`.DisruptorPlatform` :class:`.DisruptorPlatform` :math:`n` can observe interference actions of :math:`m`
        =========================== =========================== =======================================================
    

    Note
    ----
    Having a :attr:`disruptorDelay` = 0 does not currently make sense.
    Specifically, it could introduce a race condition among `Disruptor 
    Platforms`.  For example, the first `Disruptor Platform` to make a 
    decision on how to allocate `disruption tokens` would do so 
    without any knowledge of actions by other `Disruption Platforms`. 
    Then, the second `Disruption Platform` would be able to observe 
    the actions of the first `Disruption Platform` but not those of 
    any subsequent `Disruption Platforms`, and so forth.
    Therefore, by having :attr:`disruptorDelay` at least equal to 1 
    ensures that all `Disruptor Platforms` use the same knowledge and 
    observations to make their decisions.
    Alternatively, this race condition could be avoided even with a 
    delay of 0 by having all `Disruptor Platforms` act independently 
    of each other (assuming each took no action in the current time 
    step).

    Additionally, without a delay of at least 1, then the 
    `Communications Coordinator` could potentially have no chance at 
    transmitting any packets successfully through the `Environment`, 
    as any `Disruptor Platform` would immediately observe the attempted 
    packet transmission and have the opportunity to interfere with it. 
    Therefore, for `Disruptor Platforms` to be successful, they must 
    wisely use prediction to allocate `disruption tokens`.

    Note
    ----
    :attr:`commsPlatformIDs` and :attr:`disruptorPlatformIDs` are not 
    guaranteed to have jointly unique entries, but only unique entries 
    amongst themselves separately.

    Note
    ----
    The `Environment` currently implements multi-cast, where if a 
    platform transmits a packet to multiple other platforms, only 
    a single :class:`.EmissionObj` is placed in the `Environment` and 
    it will be received by multiple platforms.

    Todo
    ----
    Add support for multiple `Communications Coordinators`.
    
    Todo
    ----
    Allow :attr:`adjMatrix` to be modified automatically as a function of pair-wise platform range.

    Todo
    ----
    Add `spatial degree of freedom` in `Environment`. 
    Currently, all `platforms` share a common set of frequency bins. 
    Instead, `platforms` that have significant distance between them 
    are practically unable to be directly connected and could share 
    the same frequency bins without interfering with each other.
    """


    def __init__ ( self, theAdjMatrix, theCommsPlatforms = (), theDisruptorPlatforms = (), theNumFrequencyBins=10, theDisruptorDelay=1, theMediumAccessMethod="rr", theSlidingWindow=0.0 ):
        """
        Parameters
        ----------
        theAdjMatrix : numpy.ndarray
            The adjacency matrix indicating platform connectivity.
        theCommsPlatforms : tuple of :class:`.CommsPlatform`
            The `Communications Platforms` to be included in the 
            simulation (default ()).
        theDisruptorPlatforms : tuple of :class:`.DisruptorPlatform`
            The `Disruptor Platforms` to be included in the 
            simulation (default ()).
        theNumFrequencyBins : int
            The number of frequency bins (default 10).
        theDisruptorDelay : int
            The number of time steps behind the current time step which 
            `Disruptor Platforms` observe the status of the `Environment` 
            (default 1).
        theMediumAccessMethod : {'rr', 'tdma', 'fdma'}
            The medium access control method for the `Communications 
            Coordinator` (default 'rr').
        theSlidingWindow : float
            The number of seconds over which :attr:`trafficStatistics` is 
            computed (default 0.0).
            If equal to 0.0, then :attr:`trafficStatistics` is computed 
            for the entire simulation.
        """
        
        # Specify the communications platforms in the environment
        assert(type(theCommsPlatforms) is tuple), 'CommsPlatforms is not a tuple'
        assert(type(item) is CommsPlatform for item in theCommsPlatforms), 'CommsPlatforms are not the correct object type'
        self.commsPlatforms = theCommsPlatforms
        # Gather communications platform IDs
        self.commsPlatformIDs = tuple([thePlatform.id for thePlatform in theCommsPlatforms])
        # Ensure communications platform IDs are unique
        thePlatformIDs = set(self.commsPlatformIDs)
        assert(len(thePlatformIDs) == len(self.commsPlatforms)), "Communications platform IDs are not unique!"
        # Compute number of communications platforms
        self.numCommsPlatforms = len(self.commsPlatforms)

        # Specify the disruptors in the environment
        assert(type(theDisruptorPlatforms) is tuple), 'DisruptorPlatforms is not a tuple'
        assert(type(item) is DisruptorPlatform for item in theDisruptorPlatforms), 'DisruptorPlatforms are not the correct object type'
        self.disruptorPlatforms = theDisruptorPlatforms
        # Gather disruptor platform IDs
        self.disruptorPlatformIDs = tuple([thePlatform.id for thePlatform in theDisruptorPlatforms])
        # Ensure disruptor platform IDs are unique
        thePlatformIDs = set(self.disruptorPlatformIDs)
        assert(len(thePlatformIDs) == len(self.disruptorPlatforms)), "Disruptor platform IDs are not unique!"
        # Compute number of communications platforms
        self.numDisruptorPlatforms = len(self.disruptorPlatforms)
        
        # Specify the global connectivity/adjacency matrix
        assert(theAdjMatrix.shape == (self.numCommsPlatforms + self.numDisruptorPlatforms, self.numCommsPlatforms + self.numDisruptorPlatforms)), "Size of adjacency matrix must match number of Comms and Disruptor Platforms provided"
        self.adjMatrix = theAdjMatrix

        # Specify the number of discrete frequency bins in the environment
        if theNumFrequencyBins < 1 or type(theNumFrequencyBins) is not int:
            raise ValueError("Number of frequency bins must be an integer greater than zero.")
        self.numFrequencyBins = theNumFrequencyBins

        # Instantiate communications coordinator
        self.coordinator = [CommsCoordinator(theCommsPlatforms, theNumFrequencyBins, theMediumAccessMethod)]
        # TODO: This is a list to support multiple CommsCoordinators in the future

        # Initialize data for all frequencies
        self.data = [None] * (len(self.coordinator) + len(self.disruptorPlatforms))
        for i in range(len(self.coordinator)):
            self.data[i] = [None] * theNumFrequencyBins
        for i in range(len(self.disruptorPlatforms)):
            self.data[i+len(self.coordinator)] = [None] * theNumFrequencyBins

        # Specify the delay in number of time steps which the disruptors observe the status of the Environment
        assert(type(theDisruptorDelay) is int and theDisruptorDelay > 0), 'DisruptorDelay is not a positive integer'
        self.disruptorDelay = theDisruptorDelay
        # Initialize queue for environment status
        self.__dataQueue = queue.Queue(theDisruptorDelay)
        # self.__dataQueue.put([self.data, [self.data] * len(self.disruptorPlatforms)])
        for i in range(theDisruptorDelay):
            self.__dataQueue.put(self.__copyEnv(self.data))
        
        # Specify the sliding window size (in seconds) for traffic statistics
        assert(type(theSlidingWindow) is float and theSlidingWindow >= 0), 'Sliding window size is not a non-negative floating point number'
        self.windowSize = theSlidingWindow
        # Initialize traffic statistics matrix
        self.__trafficTx = [ [ [] for i in range(len(self.commsPlatforms)) ] for j in range(len(self.commsPlatforms)) ]
        self.__trafficRx = [ [ [] for i in range(len(self.commsPlatforms)) ] for j in range(len(self.commsPlatforms)) ]
        
        # Update platform connectivity according to adjacency matrix
        self.__updatePlatformConnectivity()

        # Initialize total elapsed simulation time
        self.elapsedTime = 0

    @property
    def trafficStatistics ( self ):
        """
        Compute the current packet/traffic statistics across all pairs 
        of `Communications Platforms`.
        The :math:`(m,n)` element is the ratio of packets successfully 
        received by platform :math:`n` from platform :math:`m` divided 
        by the number of packets transmitted by platform :math:`m` 
        intended for platform :math:`n`.
        This ratio accounts for both `disruption tokens` from 
        `Disruption Platforms` and the `adjacency matrix` not allowing 
        transmissions to be delivered.
        Matrix is square, but not necessarily symmetric.
        Each dimension of the matrix is :attr:`numCommsPlatforms`.

        Returns
        -------
        statMatrix : numpy.ndarray
            The traffic statistics matrix.
        """

        statMatrix = np.full((self.numCommsPlatforms,self.numCommsPlatforms), 0.0)
        for sourcePlatformIndex in range(self.numCommsPlatforms):
            for destPlatformIndex in range(self.numCommsPlatforms):
                if self.__trafficTx[sourcePlatformIndex][destPlatformIndex]:
                    statMatrix[sourcePlatformIndex,destPlatformIndex] = len(self.__trafficRx[sourcePlatformIndex][destPlatformIndex]) / len(self.__trafficTx[sourcePlatformIndex][destPlatformIndex])
        return statMatrix

    def step ( self, deltaT ):
        """
        Advance the simulation by ``deltaT`` seconds and onto the next 
        time step.

        Updates position, velocity, and acceleration of all platforms.
        Updates platform connectivity in case :attr:`adjMatrix` has been 
        changed by the user since the last time step.
        Obtains all `Packets` from all `Communications Coordinators` and 
        all `disruption tokens` from all `Disruptor Platforms`, 
        and places them in the designated frequency bins.
        Delivers all `Packets` and `disruption tokens` to their 
        intended recipients.

        Parameters
        ----------
        deltaT : float
            The number of seconds to advance the simulation by.
        """

        # Update position, velocity, and acceleration of all platforms
        for p in self.commsPlatforms:
            p.step(deltaT)
        for p in self.disruptorPlatforms:
            p.step(deltaT)
        
        # Update platform connectivity according to adjacency matrix
        self.__updatePlatformConnectivity()
        
        # Update elapsed simulation time
        self.elapsedTime += deltaT

        # Obtain data for all frequencies from coordinator
        for index, c in enumerate(self.coordinator):
            self.data[index] = c.step()

        # Update disruptors with Environment frequency allocation status
        theEnv = self.__dataQueue.get()
        # theEnvComm = theEnv[0:len(self.coordinator)]
        # theEnvDisruptor = theEnv[len(self.coordinator):len(theEnv)]
        for disruptorIndex, disruptor in enumerate(self.disruptorPlatforms):
            # Create copy of environment list for this disruptor
            theEnvTemp = self.__copyEnv(theEnv)
            # Remove packets from Comms Platforms that this disruptor cannot observe
            for cIndex in range(len(self.coordinator)):
                cData = theEnvTemp[cIndex]
                for packetIndex, packet in enumerate(cData):
                    if packet is not None:
                        theSourceID = packet.sourceID
                        theSourceIndex = self.commsPlatformIDs.index(theSourceID)
                        if not self.adjMatrix[theSourceIndex, disruptorIndex + self.numCommsPlatforms]:
                            cData[packetIndex] = None
            # Remove emission objects from other disruptors that this disruptor cannot observe
            for dIndex in range(self.numDisruptorPlatforms):
                dData = theEnvTemp[dIndex + len(self.coordinator)]
                for emissionIndex, emission in enumerate(dData):
                    if emission is not None:
                        theSourceID = emission.sourceID
                        theSourceIndex = self.disruptorPlatformIDs.index(theSourceID)
                        if not self.adjMatrix[theSourceIndex + self.numCommsPlatforms, disruptorIndex + self.numCommsPlatforms]:
                            dData[emissionIndex] = None
            # Update this disruptor's view of the Environment
            disruptor.env = theEnvTemp

        # Obtain disruptions from all disruptor platforms
        for pIndex, p in enumerate(self.disruptorPlatforms):
            self.data[pIndex + len(self.coordinator)] = p.getDisruptions()

        # Add actions from CommsCoordinator and Disruptors to history queue
        self.__dataQueue.put(self.__copyEnv(self.data))
        assert(self.__dataQueue.full()), "Environment history queue should always be full!"
        
        # Send data to each communication platform
        txData = [list() for i in range(self.numCommsPlatforms)]
        for platformData in self.data:
            for emissionObj in platformData:
                if emissionObj is not None:
                    # Record time emission object was transmitted into the Environment
                    emissionObj.emissionTime = self.elapsedTime
                
                    for destID in emissionObj.destID:
                        try:
                            destPlatformIndex = self.commsPlatformIDs.index(destID)
                            if emissionObj.sourceType == 0:
                                sourcePlatformIndex = self.commsPlatformIDs.index(emissionObj.sourceID)
                                # Add packet to matrix keeping track of all traffic
                                self.__trafficTx[sourcePlatformIndex][destPlatformIndex].append(emissionObj)
                            elif emissionObj.sourceType == 1:
                                sourcePlatformIndex = self.disruptorPlatformIDs.index(emissionObj.sourceID) + self.numCommsPlatforms
                            if self.adjMatrix[sourcePlatformIndex,destPlatformIndex]:
                                txData[destPlatformIndex].append(emissionObj)
                        except:
                            pass
        for index, commPlatform in enumerate(self.commsPlatforms):
            commPlatform.putData(txData[index])
        
        # Update traffic statistics
        for destPlatformIndex in range(self.numCommsPlatforms):
            isDisrupted = False
            for emissionObj in txData[destPlatformIndex]:
                if emissionObj.sourceType == 1:
                    isDisrupted = True
            for emissionObj in txData[destPlatformIndex]:
                if emissionObj.sourceType == 0:
                    sourcePlatformIndex = self.commsPlatformIDs.index(emissionObj.sourceID)
                    if not isDisrupted:
                        # Add packet to matrix keeping track of traffic that is successfully transmitted and received
                        self.__trafficRx[sourcePlatformIndex][destPlatformIndex].append(emissionObj)
        
        # Remove traffic statistics outside of sliding window
        if self.windowSize > 0:
            for sourcePlatformIndex in range(self.numCommsPlatforms):
                for destPlatformIndex in range(self.numCommsPlatforms):
                    if self.__trafficTx[sourcePlatformIndex][destPlatformIndex]:
                        while self.elapsedTime - self.__trafficTx[sourcePlatformIndex][destPlatformIndex][0].emissionTime > self.windowSize:
                            self.__trafficTx[sourcePlatformIndex][destPlatformIndex].pop(0)
                            if len(self.__trafficTx[sourcePlatformIndex][destPlatformIndex]) is 0:
                                break
                    if self.__trafficRx[sourcePlatformIndex][destPlatformIndex]:
                        while self.elapsedTime - self.__trafficRx[sourcePlatformIndex][destPlatformIndex][0].emissionTime > self.windowSize:
                            self.__trafficRx[sourcePlatformIndex][destPlatformIndex].pop(0)
                            if len(self.__trafficRx[sourcePlatformIndex][destPlatformIndex]) is 0:
                                break


    def __updatePlatformConnectivity ( self ):
        """
        Update the :attr:`.destIDs` attribute for :class:`.CommsPlatforms` 
        and update the :attr:`.commsDestIDs` attribute for 
        :class:`.DisruptorPlatforms` according to the current values 
        in :attr:`adjMatrix`.
        """

        # Update platform connectivity according to adjacency matrix
        for pIndex, p in enumerate(self.commsPlatforms):
            # Get platform list indices
            destIndices = list(np.nonzero(self.adjMatrix[pIndex, 0:self.numCommsPlatforms])[0])
            # Convert from list index to ID
            p.destIDs = self.__indexToID(destIndices)
        for pIndex, p in enumerate(self.disruptorPlatforms):
            # Get platform list indices
            destIndices = list(np.nonzero(self.adjMatrix[pIndex + self.numCommsPlatforms, 0:self.numCommsPlatforms])[0])
            # Convert from list index to ID
            p.commsDestIDs = self.__indexToID(destIndices)
    
    def __indexToID ( self, indices ):
        """
        Convert integer index into :attr:`commsPlatforms` to their 
        corresponding identification attributes :attr:`.id`.

        Parameters
        ----------
        indices : list of int
            The list of integer indices.

        Returns
        -------
        IDs : list
            The list of corresponding IDs.
        """

        IDs = [None] * len(indices)
        for idx in range(len(indices)):
            IDs[idx] = self.commsPlatformIDs[indices[idx]]
            # IDs[idx] = self.platforms[indices[idx]].id
        return IDs

    def __copyEnv ( self, theEnv ):
        """
        Make recursive copy of the environment status.
        Emission objects themselves are not copied.

        Parameters
        ----------
        theEnv : list of list
            The environment status, in the same form as :attr:`data`.
        
        Returns
        -------
        theEnvCopy : list of list
            The copy of the environment status.
        """

        # Make copy of top-level list
        theEnvCopy = theEnv.copy()
        # Make copy of second-level list
        for index, item in enumerate(theEnv):
            theEnvCopy[index] = item.copy()
        return theEnvCopy
