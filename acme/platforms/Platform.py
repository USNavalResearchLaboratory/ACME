import numpy as np
import argparse

class Platform:
    """
    Models the position, velocity, and acceleration of a platform.

    Attributes
    ----------
    id : any
        The identification for this platform.
    pos : numpy.ndarray
        The current position in cartesian coordinates.
        Array has length 3 and is specified as :math:`[p_x,p_y,p_z]`.
    vel : numpy.ndarray
        The current velocity in cartesian coordinates.
        Array has length 3 and is specified as :math:`[v_x,v_y,v_z]`.
    acc : numpy.ndarray
        The current acceleration in cartesian coordinates.
        Array has length 3 and is specified as :math:`[a_x,a_y,a_z]`.
    elapsedTime : float
        The number of simulated seconds that have passed since the 
        simulation began.
    elapsedTimeSteps : int
        The number of time steps that have passed since the 
        simulation began (i.e., number of times :meth:`step` has been 
        called).
    """

    def __init__ ( self, theID, initialPos=[0,0,0], initialVel=[0,0,0], initialAcc=[0,0,0] ):
        """
        Parameters
        ----------
        theID : any
            The identification for this platform.
            May be of any data type (int, str, etc.).
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
        
        parser = argparse.ArgumentParser(description='Verify user input.')

        self.id = theID
        
        self.pos = np.array(initialPos, dtype=np.float64)
        self.vel = np.array(initialVel, dtype=np.float64)
        self.acc = np.array(initialAcc, dtype=np.float64)

        # Initialize time elapsed counter (seconds)
        self.elapsedTime = 0
        # Initialize time step counter (number of time steps)
        self.elapsedTimeSteps = 0

    def posX ( self ):
        """
        The first position coordinate (:math:`p_x`).
        """
        return self.pos[0]
    def posY ( self ):
        """
        The second position coordinate (:math:`p_y`).
        """
        return self.pos[1]
    def posZ ( self ):
        """
        The third position coordinate (:math:`p_z`).
        """
        return self.pos[2]
    def velX ( self ):
        """
        The first velocity coordinate (:math:`v_x`).
        """
        self.vel[0]
    def velY ( self ):
        """
        The second velocity coordinate (:math:`v_y`).
        """
        return self.vel[1]
    def velZ ( self ):
        """
        The third velocity coordinate (:math:`v_z`).
        """
        return self.vel[2]
    def accX ( self ):
        """
        The first acceleration coordinate (:math:`a_x`).
        """
        return self.acc[0]
    def accY ( self ):
        """
        The second acceleration coordinate (:math:`a_y`).
        """
        return self.acc[1]
    def accZ ( self ):
        """
        The third acceleration coordinate (:math:`a_z`).
        """
        return self.acc[2]
    

    def step(self, deltaT):
        """
        Advance the platform's position, velocity, and acceleration by 
        ``deltaT`` seconds.

        Parameters
        ----------
        deltaT : float
            The number of seconds to advance the platform by.
        """

        # Update position, velocity, and acceleration
        mtx = np.array([[1, deltaT, 0.5*deltaT**2], [0, 1, deltaT], [0, 0, 1]], dtype=np.float64)
        state = np.matmul(mtx, np.concatenate([[self.pos], [self.vel], [self.acc]],axis=0))
        self.pos = state[0]
        self.vel = state[1]
        self.acc = state[2]
        
        # Update elapsed simulation time
        self.elapsedTime += deltaT
        self.elapsedTimeSteps += 1
        