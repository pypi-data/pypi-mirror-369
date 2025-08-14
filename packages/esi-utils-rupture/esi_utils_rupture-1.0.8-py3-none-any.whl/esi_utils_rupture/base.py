#!/usr/bin/env python

# stdlib modules
from abc import ABC
from abc import abstractmethod
import json

# third party imports
import numpy as np

try:
    _ = np.RankWarning  # will work on numpy < 2
except AttributeError:
    setattr(np, "RankWarning", RuntimeWarning)  # will work on numpy > 2
from openquake.hazardlib.geo import geodetic

# local imports
from esi_utils_rupture import constants


class RuptureContext:
    pass


class Rupture(ABC):
    """
    Abstract base class for ruptures.

    Note on terminology:

        - There are three Ruptuer subclasses: PointRupture, QuadRupture, and
          EdgeRupture.
        - PointRupture represents the rupture as a point source.
        - QuadRupture and EdgeRupture are two different finite source
          representations.
        - A finite rupture is composed of segments. For QuadRupture, a segment
          is a quadrilaterial; for an EdgeRupture, a segment is a line
          connecting two points.
        - Segments are grouped with a common "group index".
        - Segments within a group must be continuous.
        - The QuadRupture class requires that each segment is a quadrilateral
          with horizontal top and obttom edges.
        - The EdgeRupture class allows for arbitrarily complex top and bottom
          edge specification.

    """

    def writeGeoJson(self, file):
        """
        Write the rupture to a GeoJson file.

        Args:
            file (str): Name of file.
        """
        with open(file, "w") as f:
            json.dump(self._geojson, f)

    def getGeoJson(self):
        """
        Get the object's GeoJson
        """
        return self._geojson

    @abstractmethod
    def getLength(self):  # pragma: no cover
        """
        Returns:
            float: Rupture length in km.
        """
        raise NotImplementedError(
            "'Rupture::getLength' must be overridden by child classes"
        )

    @abstractmethod
    def getWidth(self):  # pragma: no cover
        """
        Returns:
            float: Rupture width in km.
        """
        raise NotImplementedError(
            "'Rupture::getWidth' must be overridden by child classes"
        )

    @abstractmethod
    def getArea(self):  # pragma: no cover
        """
        Returns:
            float: Rupture area in square km.
        """
        raise NotImplementedError(
            "'Rupture::getArea' must be overridden by child classes"
        )

    @abstractmethod
    def getStrike(self):  # pragma: no cover
        """
        Return strike angle. If rupture consists of multiple quadrilaterals,
        the average strike angle, weighted by quad length, is returned.
        Note: for ruptures with quads where the strike angle changes by 180 deg
        due to reverses in dip direction are problematic and not handeled well
        by this algorithm.

        Returns:
            float: Strike angle in degrees.

        """
        raise NotImplementedError(
            "'Rupture::getStrike' must be overridden by child classes"
        )

    @abstractmethod
    def getDip(self):  # pragma: no cover
        raise NotImplementedError(
            "'Rupture::getDip' must be overridden by child classes"
        )

    @abstractmethod
    def getDepthToTop(self):  # pragma: no cover
        """
        Returns:
           float: Average dip in degrees.

        """
        raise NotImplementedError(
            "'Rupture::getDepthToTop' must be overridden by child classes"
        )

    @abstractmethod
    def getQuadrilaterals(self):  # pragma: no cover
        """
        Method to return rupture quadrilaterals. Returns None for
        PointRupture.
        """
        raise NotImplementedError(
            "'Rupture::getQuadrilaterals' must be overridden by child classes"
        )

    def getReference(self):
        """
        Returns:
           string: Reference info from file.

        """
        return self._reference

    def getOrigin(self):
        """
        Returns:
           Origin object

        """
        return self._origin

    @property
    @abstractmethod
    def lats(self):  # pragma: no cover
        raise NotImplementedError(
            "'Rupture::lats' must be overridden by child classes"
        )

    @property
    @abstractmethod
    def lons(self):  # pragma: no cover
        raise NotImplementedError(
            "'Rupture::lons' must be overridden by child classes"
        )

    @property
    @abstractmethod
    def depths(self):  # pragma: no cover
        raise NotImplementedError(
            "'Rupture::depths' must be overridden by child classes"
        )

    def getRuptureContext(self, gmpelist, shape=None):
        """
        Args:
            gmpelist (list): List of hazardlib GMPE objects.
            shape (tuple): The shape of the ndarrays for each element. If "None",
                the values will be scalars.


        Returns:
            RuptureContext object with all known parameters filled in.

        """  # noqa

        origin = self._origin

        # rupturecontext constructor inputs:
        # 'mag', 'strike', 'dip', 'rake', 'ztor', 'hypo_lon', 'hypo_lat',
        # 'hypo_depth', 'width', 'hypo_loc'

        rx = RuptureContext()
        if shape is None:
            rx.mag = origin.mag
            rx.strike = self.getStrike()
            rx.dip = self.getDip()
            rx.ztor = self.getDepthToTop()
            rx.width = self.getWidth()

            if hasattr(origin, "rake"):
                rx.rake = origin.rake
            elif hasattr(origin, "mech"):
                rx.rake = constants.RAKEDICT[origin.mech]
            else:
                rx.rake = constants.RAKEDICT["ALL"]

            rx.hypo_lat = origin.lat
            rx.hypo_lon = origin.lon
            rx.hypo_depth = origin.depth
        else:
            rx.mag = np.full(shape, origin.mag)
            rx.strike = np.full(shape, self.getStrike())
            rx.dip = np.full(shape, self.getDip())
            rx.ztor = np.full(shape, self.getDepthToTop())
            rx.width = np.full(shape, self.getWidth())

            if hasattr(origin, "rake"):
                rx.rake = np.full(shape, origin.rake)
            elif hasattr(origin, "mech"):
                rx.rake = np.full(shape, constants.RAKEDICT[origin.mech])
            else:
                rx.rake = np.full(shape, constants.RAKEDICT["ALL"])

            rx.hypo_lat = np.full(shape, origin.lat)
            rx.hypo_lon = np.full(shape, origin.lon)
            rx.hypo_depth = np.full(shape, origin.depth)

        return rx

    def computeRhyp(self, lon, lat, depth):
        """
        Method for computing hypocentral distance.

        Args:
            lon (array): Numpy array of longitudes.
            lat (array): Numpy array of latitudes.
            depth (array): Numpy array of depths (km; positive down).

        Returns:
           array: Hypocentral distance (km).
        """
        origin = self._origin
        oldshape = lon.shape

        rhyp = geodetic.distance(
            origin.lon, origin.lat, origin.depth, lon, lat, depth
        )
        rhyp = rhyp.reshape(oldshape)
        return rhyp

    def computeRepi(self, lon, lat, depth):
        """
        Method for computing epicentral distance.

        Args:
            lon (array): Numpy array of longitudes.
            lat (array): Numpy array of latitudes.
            depth (array): Numpy array of depths (km; positive down).

        Returns:
           array: Epicentral distance (km).
        """
        origin = self._origin
        oldshape = lon.shape

        repi = geodetic.distance(origin.lon, origin.lat, 0.0, lon, lat, depth)
        repi = repi.reshape(oldshape)
        return repi

    @abstractmethod
    def computeRjb(self, lon, lat, depth):  # pragma: no cover
        """
        Method for computing Joyner-Boore distance.

        Args:
            lon (array): Numpy array of longitudes.
            lat (array): Numpy array of latitudes.
            depth (array): Numpy array of depths (km; positive down).

        Returns:
           array: Joyner-Boore distance (km).

        """
        pass

    @abstractmethod
    def computeRrup(self, lon, lat, depth):  # pragma: no cover
        """
        Method for computing rupture distance.

        Args:
            lon (array): Numpy array of longitudes.
            lat (array): Numpy array of latitudes.
            depth (array): Numpy array of depths (km; positive down).

        Returns:
           array: Rupture distance (km).

        """
        pass

    @abstractmethod
    def computeGC2(self, lon, lat, depth):  # pragma: no cover
        """
        Method for computing version 2 of the Generalized Coordinate system
        (GC2) by Spudich and Chiou OFR 2015-1028.

        Args:
            lon (array): Numpy array of longitudes.
            lat (array): Numpy array of latitudes.
            depth (array): Numpy array of depths (km; positive down).

        Returns:
            dict: Dictionary with keys for each of the GC2-related distances,
                which include 'rx', 'ry', 'ry0', 'U', 'T'.
        """
        pass
