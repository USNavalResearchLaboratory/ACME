from .Platform import Platform
from ..EmissionObj import Packet
from ..EmissionObj import AckPacket
from ..EmissionObj import DisruptionToken
import queue
import warnings
import copy

class CommsPlatform(Platform):
    """
    Models a `Communications Platform` that can transmit and receive 
    units of information (`Packets`).

    Attributes
    ----------
    destIDs : list
        The list of identification attributes :attr:`.id` for all 
        platforms that this platform may transmit to.
    doAck : boolean
        Indication whether to place acknowledgement packets into the 
        transmit queue when data packets are received and placed into 
        the receive queue.
    
    Todo
    ----
    Implement a learning mechanism to automatically determine which 
    other platforms this platform is connected to.
    Currently, this value is populated with ground-truth values from :attr:`.Environment.adjMatrix`.
    """
    
    def __init__ ( self, theID, theMaxSize=100, theDoAck = True, initialPos=[0,0,0], initialVel=[0,0,0], initialAcc=[0,0,0] ):
        """
        Parameters
        ----------
        theID : any
            The identification for this platform.
            May be of any data type (int, str, etc.).
        theMaxSize : int
            The maximum number of information units that can be 
            buffered in each of this platform's transmit and receive 
            queues.
            If the transmit buffer is full, then any new packets 
            requested to be transmitted will be dropped.
            If the receive buffer is full, then any new packets 
            received will be dropped.
        theDoAck : boolean
            Indicate whether to transmit :class:`.AckPackets` upon 
            receiving :class:`.Packets`.
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

        # Initialize array of destination IDs
        self.destIDs = []

        # Initialize FIFO data buffer/queue
        if theMaxSize < 1:
            raise ValueError("Maximum transmit queue size must be greater than zero.")
        self.txQueue = queue.Queue(theMaxSize)
        self.rxQueue = queue.Queue(theMaxSize)

        # Specify if node should create acknowledgement packets when data packets are received
        self.doAck = theDoAck

        # Initialize message ID value
        self.__currentMsgID = 1

    @property
    # Specify array of destination IDs that this object can transmit to
    def destIDs(self):
        return self.__destIDs
    @destIDs.setter
    def destIDs(self, value):
        if type(value) is not list:
            raise ValueError("Node IDs must be specified as a list of values.")
        #for i in value:
        #    if type(i) is not int:
        #        raise ValueError("Node IDs must be specified as a list of integers.")
        self.__destIDs = value

    
    def txData ( self, thePayload, theDestID ):
        """
        Send data (information unit) to another :class:`.CommsPlatform`.

        Parameters
        ----------
        thePayload : any
            The user data to become the :attr:`.payload` of a 
            :class:`.Packet` to be transmitted.
        theDestID : list
            The list of identification attributes :attr:`.id` for all 
            platforms ``thePayload`` is to be transmitted to.

        Note
        ----
        Entries in ``theDestID`` are not required to be entries in 
        :attr:`destIDs`.  If they are not, then `packets` will still 
        be constructed and transmitted, but just not delivered to any 
        platform.
        """

        # To be called by the user to transmit data

        # Error checking
        assert(type(theDestID) is list), 'theDestIDs is not a list'
        #assert(all(elem in self.destIDs for elem in theDestID)), "theDestID is not valid"

        # Only send to valid destination IDs (take set intersection)
        #theDestID = list(set(theDestID) & set(self.destIDs))

        # Create packet to transmit
        theMsgID = self.__getNextMsgID()
        # Make deep-copy of payload
        thePayloadCopy = copy.deepcopy(thePayload)
        thePacket = Packet(self.id, theDestID, self.elapsedTime, thePayloadCopy, theMsgID)
        self.__txPacket(thePacket)
    
    def rxData ( self ):
        """
        Obtain the next payload in this platform's receive queue.
        May be called repeatedly by the user.

        Returns
        -------
        thePayload : any
            The next payload in this platform's receive queue.
            Returns ``None`` if the receive queue is empty.

        Example
        -------
        If the user wants to empty the receive queue within the 
        current time step::

            thePayload = thePlatform.rxData()
            while thePayload is not None:
                thePayload = thePlatform.rxData()
        """

        # To be called by the user to query for data that has been received
        if self.rxQueue.empty():
            thePayloadTemp = None
        else:
            thePayloadTemp = self.rxQueue.get()
        # Make deep-copy of payload
        thePayload = copy.deepcopy(thePayloadTemp)
        return thePayload
    
    def getData ( self ):
        """
        Obtain the next :class:`.Packet` in the transmit queue to be 
        transmitted.

        Returns
        -------
        thePacket : :class:`.Packet`
            The :class:`.Packet` to be transmitted.

        Warning
        -------
        Method is typically called automatically by the 
        :class:`.CommsCoordinator` and is not intended to be called 
        directly by the user.
        """

        # To be called by the CommsCoordinator each time step
        # Get data to transmit
        if self.txQueue.empty():
            thePacket = None
        else:
            thePacket = self.txQueue.get()
        return thePacket

    def putData ( self, theEmissionList ):
        """
        Process `emission objects` that have been received and place 
        them in the receive queue.
        Do not place any `acknowledgement packets` that have been received 
        into the receive queue.
        If any of these `emission objects` is a `disruption token`, 
        then all `emission objects` will be dropped and not processed.
        Additionally, place new `acknowledgement packets` in the 
        transmit queue if configured to do so.

        Parameters
        ----------
        theEmissionList : list
            List of :class:`.EmissionObj` that have been received.
        
        Warning
        -------
        Method is typically called automatically by the 
        :class:`.Environment` and is not intended to be called 
        directly by the user.
        """

        # To be called by the Environment each time step
        
        # Determine if packets should be dropped due to disruptions
        isDisrupted = False
        for thePacket in theEmissionList:
            if isinstance(thePacket, DisruptionToken):
                isDisrupted = True
        if isDisrupted:
            return

        for thePacket in theEmissionList:
            # Drop acknowledgement packets
            if isinstance(thePacket, AckPacket):
                continue

            # Add packet to receive queue
            if self.rxQueue.full():
                warnings.warn("Receive queue for PlatformID {} is full.  Data is dropped.".format(self.id))
            else:
                self.rxQueue.put(thePacket.payload)
                if self.doAck:
                    #assert(thePacket.sourceID in self.destIDs), "Communication is not bi-directional. Cannot send acknowledgements."
                    theMsgID = self.__getNextMsgID()
                    theAckPacket = AckPacket(self.id, [thePacket.sourceID], self.elapsedTime, thePacket.msgID, theMsgID)
                    self.__txPacket(theAckPacket)

    def __txPacket ( self, thePacket ):
        """
        Add packet to transmit queue.

        Parameters
        ----------
        thePacket : :class:`.Packet`
            The :class:`.Packet` to add to the platform's transmit queue.
        """

        if self.txQueue.full():
            warnings.warn("Transmit queue for PlatformID {} is full.  Data is dropped.".format(self.id))
        else:
            self.txQueue.put(thePacket)

    def __getNextMsgID ( self ):
        """
        Obtain the next available unique message ID for the next Packet

        Returns
        -------
        theMsgID : int
            The next unique message ID
        """

        theMsgID = self.__currentMsgID
        self.__currentMsgID += 1
        return theMsgID
