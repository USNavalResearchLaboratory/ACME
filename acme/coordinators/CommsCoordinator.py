class CommsCoordinator:
    """
    Implements the medium access control (MAC) layer.

    Coordinates incoming units of information from multiple 
    `Communications Platforms` and decides how to place these 
    information units into the `RF Environment` for transmission.

    Warning
    -------
    This class is typically instantiated automatically by the 
    :class:`.Environment` and is generally not instantiated directly 
    by the user.

    Attributes
    ----------
    platforms : tuple of :class:`.CommsPlatform`
        The tuple containing the `Communications Platforms` that this 
        Coordinator manages.
    platformIDs : list
        The list of the property :attr:`.id` from all `Communications 
        Platforms` in :attr:`platforms`.
    numPlatforms : int
        The number of `Communication Platforms` controlled by this 
        entity (i.e., the length of :attr:`platforms`).
    numFrequencyBins : int
        The number of frequency bins in the :class:`.Environment`.
    mac : {'rr', 'tdma', 'fdma'}
        The medium access control method.
    
    Todo
    ----
    Implement more `medium access control` protocols.

    Todo
    ----
    Implement routing mechanism so that packets may be delivered via 
    relay platforms instead of only point-to-point links.
    """

    def __init__ ( self, thePlatforms, theNumFrequencyBins, theMediumAccessMethod ):
        """
        Parameters
        ----------
        thePlatforms : tuple of :class:`.CommsPlatform`
            Tuple containing the `Communications Platforms` that this 
            Coordinator will manage.
        theNumFrequencyBins : int
            The number of frequency bins in the :class:`.Environment`.
        theMediumAccessMethod : {'rr', 'tdma', 'fdma'}
            The medium access control method.

            ====== ==================================
            String Description
            ====== ==================================
            rr     round robin
            tdma   time division multiple access
            fdma   frequency division multiple access
            ====== ==================================
        """

        # Specify the communications platforms to coordinate
        self.platforms = thePlatforms
        # Gather communications platform IDs
        self.platformIDs = [thePlatform.id for thePlatform in thePlatforms]
        # Compute number of communications platforms
        self.numPlatforms = len(self.platforms)

        # Specify the number of discrete frequency bins in the environment
        if theNumFrequencyBins < 1 or type(theNumFrequencyBins) is not int:
            raise ValueError("Number of frequency bins must be an integer greater than zero.")
        self.numFrequencyBins = theNumFrequencyBins
        
        # Specify the medium access control method
        self.mac = theMediumAccessMethod
        
        # Initialize TDMA index
        self.__TDMAindex = 0

    
    def step ( self ):
        """
        Obtain the next set of information units from all entities in 
        :attr:`platforms` for the current time step.
        Intended to be called once per time step.

        Returns
        -------
        txPackets : list of :class:`.Packet`
            List of :class:`.Packet` corresponding to which information 
            units have been placed in which frequency bins.
            Each element of the list is either ``None`` or contains a 
            single :class:`.Packet`.
            List has length :attr:`numFrequencyBins`.
        
        Warning
        -------
        This method is typically called automatically by the 
        :class:`.Environment` and is generally not called directly by 
        the user.
        """

        if self.mac == "rr":
            txPackets = self.__stepRoundRobin()
        elif self.mac == "tdma":
            txPackets = self.__stepTDMA()
        elif self.mac == "fdma":
            txPackets = self.__stepFDMA()
        else:
            raise ValueError("Invalid medium access control method")

        # Assign position and frequency bin index to each packet
        for binIndex, packet in enumerate(txPackets):
            # Assign frequency bin index
            if packet:
                packet.freqBin = binIndex
                # Get platform index
                platformIndex = self.platformIDs.index(packet.sourceID)
                # Assign emission/platform position
                packet.position = self.platforms[platformIndex].pos

        return txPackets
    

    def __stepRoundRobin ( self ):
        """
        Perform `round robin` protocol.

        Returns
        -------
        txPackets : list of :class:`.Packet`
        """

        # Frequency bins are filled only as platforms actually have data to transmit
        txPackets = [None] * self.numFrequencyBins
        index = 0
        for p in self.platforms:
            theData = p.getData()
            if theData:
                txPackets[index] = theData
                index += 1
            if index == self.numFrequencyBins:
                # There are more platforms with data to transmit than there are frequency bins
                # Cannot transmit all data
                break
        return txPackets


    def __stepTDMA ( self ):
        """
        Perform `TDMA` protocol.

        Returns
        -------
        txPackets : list of :class:`.Packet`
        """

        # Only one platform can transmit at a time

        # Only one frequency bin may exist
        if self.numFrequencyBins != 1:
            raise ValueError("When using TDMA, only one frequency bin can exist.")

        p = self.platforms[self.__TDMAindex]
        txPackets = [p.getData()]

        # Increment TDMA index to next platform
        self.__TDMAindex += 1
        if self.__TDMAindex == self.numPlatforms:
            self.__TDMAindex = 0        

        return txPackets


    def __stepFDMA ( self ):
        """
        Perform `FDMA` protocol.

        Returns
        -------
        txPackets : list of :class:`.Packet`
        """

        # Each platform gets a fixed frequency bin
        
        # There must be at least as many frequency bins as platforms
        if self.numFrequencyBins < self.numPlatforms:
            raise ValueError("When using FDMA, the number of frequency bins must be at least the number of platforms.")

        txPackets = [None] * self.numFrequencyBins
        for index, p in enumerate(self.platforms):
            txPackets[index] = p.getData()
        return txPackets
