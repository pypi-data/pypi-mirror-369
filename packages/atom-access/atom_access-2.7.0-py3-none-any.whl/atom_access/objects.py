'''
This submodule contains ray and sphere objects and methods used for raytracing
'''

import numpy as np
import numpy.typing as npt
import numpy.linalg as la

from . import utils as ut


class Sphere:
    '''
    Contains all information required to define a sphere and to calculate\n
    its intersection with a ray

    Parameters
    ----------
    radius: float
        Radius of sphere
    center: np.ndarray[float]
        x,y,z coordinates of sphere center
    name: str
        Name of sphere (e.g Atom label with indexing number)

    Attributes
    ----------
    radius: float
        Radius of sphere
    radius2: float
        Squared radius of sphere
    center: np.ndarray[float]
        x,y,z coordinates of sphere center
    center_dist: np.ndarray[float]
        Distance to center from origin
    name: str
        Name of sphere (e.g Atom label with indexing number)
    '''
    __slots__ = 'radius', 'radius2', 'center', 'center_dist', 'name'

    def __init__(self, radius: float, center: npt.NDArray, name: str):

        self.radius = radius
        self.radius2 = radius**2
        self.center = center
        self.center_dist = la.norm(self.center)
        self.name = name

        return

    def intersect(self, ray: 'Ray') -> tuple[bool, float, float]:
        '''
        Calculate intersection points of normalised ray vector with\n
        sphere if they exist.

        Parameters
        ----------
        ray: Ray
            Ray object

        Returns
        -------
        bool
            True if intersection, else False
        float
            First intersection point, 0 if no intersection
        float
            Second intersection point, 0 if no intersection
        '''

        # Find projection of ray onto sphere centre-origin vector
        p = np.dot(self.center, ray.cart)

        if p < 0.:
            return False, 0., 0.
        # Find minimum sphere centre to ray distance (squared)
        d2 = self.center_dist**2 - p**2
        if d2 > self.radius2:
            return False, 0., 0.
        t = np.sqrt(self.radius2 - d2)

        # Find ray-sphere intersection points
        # These are scalars used in the vector equation of line
        # P1 = O + (p-t)*uhat
        # P2 = O + (p+t)*uhat
        # where P1 is intersection point on the ray, uhat is the
        # normalised ray vector, and O is a point in space,
        # in this case the origin
        p1 = p - t
        p2 = p + t

        return True, p1, p2


class Ray:
    '''
    Contains all information required to define a ray of light and its\n
    intersection with an object. A ray is defined by its polar and azimuthal\n
    angles, is assumed to have unit length, and passes through the origin.

    Parameters
    ----------
    theta: float
        Polar angle 0 <= theta <= pi
    phi: float
        Azimuthal angle 0 <= phi <= 2pi


    Attributes
    ----------
    theta: float
        Polar angle 0 <= theta <= pi
    phi: float
        Azimuthal angle 0 <= phi <= 2pi
    r: float
        Length of ray, assumed unity (ray is normalised)
    x: float
        x component of ray vector in cartesian coordinates
    y: float
        y component of ray vector in cartesian coordinates
    z: float
        z component of ray vector in cartesian coordinates
    cart: np.ndarray[float]
        Direction vector of ray as (3,) np.array
    intersection: bool
        True if ray intersects with object
    r_i: float
        Distance of closest intersection point from origin.\n
        If no intersection, then this is set to np.inf.
    cart_i: np.ndarray[float]
        Position vector of closest intersection point as (3,) np.array
    blocked_by: list(str)
        List of atom labels the ray intersects with, with the closest\n
        listed first

    '''
    __slots__ = [
        'theta', 'phi', 'x', 'y', 'z', 'intersection', 'r', 'r_i', 'cart',
        'cart_i', 'blocked_by'
    ]

    def __init__(self, theta: float, phi: float):

        # Spherical coordinates
        self.theta = theta
        self.phi = phi
        self.r = 1.

        # Cartesian coordinates
        st = np.sin(self.theta)
        self.x = self.r * st * np.cos(self.phi)
        self.y = self.r * st * np.sin(self.phi)
        self.z = self.r * np.cos(self.theta)
        self.cart = np.array([self.x, self.y, self.z])

        # Intersection point
        self.intersection = False

        return

    @property
    def intersection(self) -> bool:
        '''
        True if ray intersects with object, else False
        '''
        return self._intersection

    @intersection.setter
    def intersection(self, value: bool) -> None:
        # Set intersection status of ray
        self._intersection = value
        # Reset intersection distance, position vector, and blocking atoms
        self.r_i = np.inf
        self.cart_i = np.array([0., 0., 0.])
        self.blocked_by = []
        return

    @classmethod
    def from_zcw(cls, density: int) -> list['Ray']:
        '''
        Generate a set of rays emanating from a single point using the ZCW\n
        algorithm\n\n

        See Appendix I in\n
        Edén, M.; Levitt, M. H. J. Magn. Res., 1998, 132, 220-239.

        Parameters
        ----------
        density : int
            Density number for ZCW algorithm

        Returns
        -------
        list[Ray]
            List of ray objects
        '''

        density = int(density)

        g = [ut.recursive_g(m) for m in range(density + 3)]
        N = g[density + 2]

        c = [1, 2, 1]

        rays = [
            cls(
                np.arccos(c[0] * (c[1] * np.fmod(j / N, 1) - 1)),
                2 * np.pi / c[2] * np.fmod(j * g[density] / N, 1)
            ) for j in range(N)
        ]

        return rays

    def calc_cart_i(self) -> None:
        '''
        Calculates position vector of intersection point using intersection\n
        distance

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        self.cart_i = self.cart * self.r_i

        return
