# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TTCoordinateCapturer
                                 A QGIS plugin
 It's use to capture the cooridnates on Map Canvas.
                             -------------------
        begin                : 2016-05-30
        copyright            : (C) 2016 by Miles TOMTOM
        email                : miles.lee@tomtom.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load TTCoordinateCapturer class from file TTCoordinateCapturer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .coordinate_capturer import TTCoordinateCapturer
    return TTCoordinateCapturer(iface)
