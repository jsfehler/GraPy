import math

from .constants import Constants


def findDistance(node1, node2):
    """finds the distance as a scalar (the hypot of the x and y positions)
    """
    d = math.hypot(
        (node2.position[0] - node1.position[0]),
        (node2.position[1] - node1.position[1]))
    return d


def findDistanceTuple(node1, node2):
    return (
        node2.position[0] - node1.position[0] + 0.01,
        node2.position[1] - node1.position[1] + 0.01)


def findAngle(node1, node2):
    distanceTuple = findDistanceTuple(node1, node2)
    return math.atan2(distanceTuple[1], distanceTuple[0])


class Node:
    """Contains a UID and some properties to define its location in space.

    A Node knows only of itself, so has no knowledge of which nodes it is
    connected to.

    A Node calculates all forces that would act upon itself,
    never the forces that would act upon another node.
    """

    data = []

    acceleration = (0.0, 0.0)

    _forcelist = []

    charge = 1.0

    radius = 9

    def __init__(self, uid,
                 position=(0.0, 0.0), velocity=(0.0, 0.0), mass=1,
                 static=False, charge=10, boundingbox=((-5, -5), (5, 5)),
                 neighbours=[]):
        self.UID = uid
        self.position = position
        self.velocity = velocity
        self.mass = mass
        self.static = static
        self.charge = charge
        self.boundingbox = boundingbox
        self.neighbours = neighbours

    # these methods find the force acting on SELF given the other node, not the forces self is producing on the other node.
    # when we say force we are referring to a tuple with x and y values in that order
    # a force represents the actual direction of travel of the node, so we don't need to negate the force before applying it or anything
    def calculateAttractiveForce(self, other):
        forcemagnitude = self._calcAttractiveForceMagnitude(other)
        distanceangle = findAngle(self, other)

        forcex = math.cos(distanceangle) * forcemagnitude
        forcey = math.sin(distanceangle) * forcemagnitude

        return (forcex, forcey)

    # calculates the total value of the attractive force
    def _calcAttractiveForceMagnitude(self, other):
        distance = findDistance(self, other)
        # we should perhaps add in a minimum string length later on.
        return Constants.ATTRACTIVE_FORCE_CONSTANT * (distance - Constants.MINIMUM_SPRING_SIZE)

    def calculateRepulsiveForce(self, other):
        forcemagnitude = self._calcRepulsiveForceMagnitude(other)
        distanceangle = findAngle(self, other)

        forcex = math.cos(distanceangle) * forcemagnitude
        forcey = math.sin(distanceangle) * forcemagnitude

        return (forcex, forcey)

    # a function similar to that of gravitation; a parabolic fall off.
    # the distance^2 + charge*charge part means it can never
    # exceed the repulsive force constant
    def _calcRepulsiveForceMagnitude(self, other):
        distance = findDistance(self, other)
        if distance < 15:
            distance = 15
        charge = self.charge * other.charge
        return -Constants.REPULSIVE_FORCE_CONSTANT * 1.0 * charge / ((distance * 0.2)**2 + charge)

    def calculateAttractiveForces(self, nodeslist):
        return map(self.calculateAttractiveForce, nodeslist)

    def calculateRepulsiveForces(self, nodeslist):
        return map(self.calculateRepulsiveForce, nodeslist)

    def applyForce(self, force):
        self._forcelist = self._forcelist + [force]

    def applyForces(self, forcelist):
        map(applyforce, forcelist)

    # calculates the frictional force but does not apply it
    def calculateFrictionalForce(self):
        friction = -Constants.FRICTION_COEFFICIENT * self.mass

        return (
            self.velocity[0] * friction,
            self.velocity[1] * friction
        )

    def move(self, framerate):
        """Takes the framerate of the simulation.

        This should be an unchanging/static framerate,
        and should ideally not fluctuate.
        """
        if not self.static:
            self.applyForce(self.calculateFrictionalForce())

            totalforce = (0.0, 0.0)
            for f in self._forcelist:
                totalforce = (totalforce[0] + f[0], totalforce[1] + f[1])

            self.acceleration = (
                self.acceleration[0] + (totalforce[0] / self.mass),
                self.acceleration[1] + (totalforce[1] / self.mass))

            self.velocity = (
                self.velocity[0] + self.acceleration[0] / framerate,
                self.velocity[1] + self.acceleration[1] / framerate)

            frictionalcoefficient = Constants.PER_FRAME_FRICTION_COEFFICIENT
            self.velocity = (
                self.velocity[0] * frictionalcoefficient,
                self.velocity[1] * frictionalcoefficient)

            self.position = (
                self.position[0] + self.velocity[0] / framerate,
                self.position[1] + self.velocity[1] / framerate)

        self.acceleration = (0.0, 0.0)
        self._forcelist = []
