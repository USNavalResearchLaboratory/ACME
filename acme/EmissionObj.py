class EmissionObj:
    """
    Abstract class for any unit of information to be emitted.
    
    Super-class for all emission objects to be transmitted by any 
    `Platform`, whether a :class:`.CommsPlatform` or 
    :class:`.DisruptorPlatform`.

    Attributes
    ----------
    sourceID : any
        The identification attribute :attr:`.id` of the source 
        :class:`.Platform`.
    sourceType : int
        The integer indicating the type of source platform.

        ============== ===========================
        ``sourceType`` Description
        ============== ===========================
        0              :class:`.CommsPlatform`
        1              :class:`.DisruptorPlatform`
        ============== ===========================

    destID : any
        The identification attribute :attr:`.id` of the destination 
        :class:`.CommsPlatform`.
    time : float
        The time at which this object was created and placed into a 
        platform's transmit queue.
    emissionTime : float
        The time at which this object was placed into a frequency bin 
        in the :class:`.Environment`.
    freqBin : int
        The frequency bin index in which this object is placed in the 
        :class:`.Environment`.  Number is in the range [0, :attr:`~.Environment.numFrequencyBins`-1].
    position : numpy.ndarray
        The position of the platform (:attr:`.pos`) at the time this 
        object was placed in the :class:`.Environment`.
    """

    def __init__ ( self, theSourceID, theDestID, theTime ):
        """
        Parameters
        ----------
        theSourceID : any
            The identification attribute :attr:`.id` of the source 
            :class:`.Platform`.
        theDestID : any
            The identification attribute :attr:`.id` of the 
            destination :class:`.CommsPlatform`.
        theTime : float
            The time at which this object was created.
        """

        # Make this an Abstract class (cannot instantiate)
        if type(self) is EmissionObj:
            raise Exception('This is an abstract class and cannot be instantiated directly.')
        
        self.sourceID = theSourceID
        self.destID = theDestID
        self.time = theTime         # Creation time
        self.emissionTime = None    # Time object is emitted into Environment (will be updated by Environment)

        # Will be populated later by CommsCoordinator or DisruptorPlatform
        self.freqBin = 0
        self.position = None

        # Assign source platform type
        if type(self) is Packet or type(self) is AckPacket:
            self.sourceType = 0     # This indicates CommsPlatform
        elif type(self) is DisruptionToken:
            self.sourceType = 1     # This indicates DisruptorPlatform
        else:
            raise Exception('Unknown emission type.')


class Packet(EmissionObj):
    """
    Implements an `information unit` to be transmitted by any 
    :class:`.CommsPlatform` to another :class:`.CommsPlatform`.

    Attributes
    ----------
    payload : any
        The user data payload to be transmitted.
    msgID : int
        The message ID number for this `information unit`.
    """

    def __init__ ( self, theSourceID, theDestID, theTime, thePayload, theMsgID ):
        """
        Parameters
        ----------
        theSourceID : any
            The identification attribute :attr:`.id` of the source 
            :class:`.Platform`.
        theDestID : any
            The identification attribute :attr:`.id` of the 
            destination :class:`.CommsPlatform`.
        theTime : float
            The time at which this object was created.
        thePayload : any
            The user data to be transmitted.
        theMsgID : int
            The message ID number for this object.
        """

        super().__init__( theSourceID, theDestID, theTime )
        self.payload = thePayload
        self.msgID = theMsgID


class AckPacket(Packet):
    """
    Implements a specific type of information unit to be transmitted
    by a :class:`.CommsPlatform` to acknowledge the receipt of a 
    :class:`Packet` from another :class:`.CommsPlatform`.
    
    The :attr:`~EmissionObj.destID` and :attr:`~Packet.payload` of 
    this object are the :attr:`~EmissionObj.sourceID` and 
    :attr:`~Packet.msgID`, respectively, of the :class:`Packet` that 
    was successfully received.
    """
    
    def __init__ ( self, theSourceID, theDestID, theTime, thePayload, theMsgID ):
        # For acknowledgement packets, the payload is the message ID of the Packet that is being acknowledged
        super().__init__( theSourceID, theDestID, theTime, thePayload, theMsgID )


class DisruptionToken(EmissionObj):
    """
    Implements a disruption token to be transmitted by a 
    :class:`.DisruptorPlatform` to interfere with a :class:`Packet` 
    and cause it to not be delivered.
    """
    
    def __init__ ( self, theSourceID, theDestID, theTime ):
        super().__init__( theSourceID, theDestID, theTime )
