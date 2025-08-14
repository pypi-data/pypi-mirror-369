#!/usr/bin/env python

# third party imports
import numpy as np
import scipy.interpolate as spint
import logging

from esi_utils_time.ancient_time import HistoricTime
from esi_utils_rupture.base import Rupture
from esi_utils_rupture import constants


class PointRupture(Rupture):
    """
    Rupture class for point sources. The purpose is to gracefully handle:

        - Requests for rupture distances when no rupture is available.
        - Provide reasonable default values for rupture parameters.
    """

    def __init__(self, origin, reference="Origin"):
        """
        Constructs a PointRupture instance.

        Args:
            origin (Origin): Reference to a ShakeMap Origin instance.
            reference (str): Citable reference for rupture; in the case of a
                PointRupture, the 'reference' is probably the origin.

        Returns:
            PointRupture instance.
        """
        self._origin = origin
        self._reference = reference

        coords = [origin.lon, origin.lat, origin.depth]

        d = {
            "type": "FeatureCollection",
            "metadata": {"reference": reference},
            "features": [
                {
                    "type": "Feature",
                    "properties": {"rupture type": "rupture extent"},
                    "geometry": {"type": "Point", "coordinates": coords},
                }
            ],
        }

        # Add origin information to metadata
        odict = origin.__dict__
        for k, v in odict.items():
            if isinstance(v, HistoricTime):
                d["metadata"][k] = v.strftime(constants.TIMEFMT)
            else:
                d["metadata"][k] = v

        self._geojson = d
        #
        # Use Wells and Coppersmith (1994) to compute some basic
        # fault parameter based on the magnitude. Use the "All"
        # fault type since if this is a point rupture we probably
        # don't know much.
        #
        width = -1.01 + 0.32 * origin.mag
        self.faultWidth = np.power(10.0, width)
        area = -3.49 + 0.91 * origin.mag
        self.faultArea = np.power(10.0, area)
        self.faultLength = self.faultArea / self.faultWidth

    def getLength(self):
        """
        Return the W&C value based on magnitude.
        """
        return self.faultLength

    def getWidth(self):
        """
        Rupture width.
        Return the W&C value based on magnitude
        """
        return self.faultWidth

    def getArea(self):
        """
        Rupture area
        Return the W&C value based on magnitude
        """
        return self.faultArea

    def getStrike(self):
        """
        Strike, which is None.
        Could potentially get from strec or something?
        """
        return constants.DEFAULT_STRIKE

    def getDip(self):
        """
        Dip, which is None.
        Could potentially get from strec or something?
        """
        return constants.DEFAULT_DIP

    def getDepthToTop(self):
        """
        Depth to top of rupture.
        Use the Kaklamanos et al. (2011) formula:
            ztor = max((Zhyp - 0.6W * sin(delta)), 0)
        with the width coming from W&C 1994 as above.
        The default dip is 90, so we're reduced to:
        """
        ztor = min(30.0, max(self._origin.depth - 0.6 * self.faultWidth, 0))
        return ztor

    def getQuadrilaterals(self):
        return None

    @property
    def lats(self):
        """
        Returns rupture latitudes, which is just the hypocenter for a
        PointRupture."""
        return self._origin.lat

    @property
    def lons(self):
        """
        Returns rupture longitudes, which is just the hypocenter for a
        PointRupture."""
        return self._origin.lon

    @property
    def depths(self):
        """
        Returns rupture depths, which is just the hypocenter for a
        PointRupture."""
        return self._origin.depth

    def computeRjb(self, lon, lat, depth):
        """
        Return epicentral distances.

        Args:
            lon (array): Numpy array of longitudes.
            lat (array): Numpy array of latitudes.
            depth (array): Numpy array of depths (km; positive down).

        Returns:
            array: an array of epicentral distances.
        """
        return self.computeRepi(lon, lat, depth)

    def computeRrup(self, lon, lat, depth):
        """
        Return hypocentral distances.

        Args:
            lon (array): Numpy array of longitudes.
            lat (array): Numpy array of latitudes.
            depth (array): Numpy array of depths (km; positive down).

        Returns:
            array: and array of hypocentral distances
        """
        return self.computeRhyp(lon, lat, depth)

    def computeGC2(self, lon, lat, depth):
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
        # This just returns defaults of zero, which will hopefully behave
        # gracefully as used in GMPEs but should eventually be updated
        # so that things like the hangingwall terms are unbiased.
        gc2 = {
            "rx": np.zeros_like(lon),
            "ry": np.zeros_like(lon),
            "ry0": np.zeros_like(lon),
            "U": np.zeros_like(lon),
            "T": np.zeros_like(lon),
        }
        return gc2
