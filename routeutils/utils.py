"""Classes to be used by the Routing WS for EIDA.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

   :Copyright:
       2014-2020 Javier Quinteros, Deutsches GFZ Potsdam <javier@gfz-potsdam.de>
   :License:
       GPLv3
   :Platform:
       Linux

.. moduleauthor:: Javier Quinteros <javier@gfz-potsdam.de>, GEOFON, GFZ Potsdam
"""

import os
import datetime
import fnmatch
import json
import xml.etree.cElementTree as ET
from time import sleep
from collections import namedtuple
import logging
from copy import deepcopy
import pickle
import configparser
import urllib.request as ul
from urllib.parse import urlparse
from urllib.error import URLError
# from urllib.error import HTTPError


# I need to find a mapping from (service, URL) to the schema below. It seems
# that it could be feasible to put all routes in the datasets item

# eidaDCs = list()

# eidaDCs = [
#     {
#         "name": "GEOFON",
#         "website": "https://geofon.gfz-potsdam.de/",
#         "fullName": "GEOFON Program",
#         "summary": "The GEOFON Program at the GFZ in Potsdam",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "https://geofon.gfz-potsdam.de/waveform/",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://geofon.gfz-potsdam.de/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://geofon.gfz-potsdam.de/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://geofon.gfz-potsdam.de/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "ODC",
#         "website": "https://www.orfeus-eu.org/",
#         "fullName": "ORFEUS Data Centre",
#         "summary": "ORFEUS Data Centre at KNMI in De Bilt",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "https://www.orfeus-eu.org/data/eida/",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://www.orfeus-eu.org/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://www.orfeus-eu.org/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://www.orfeus-eu.org/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "RESIF",
#         "website": "https://www.resif.fr",
#         "fullName": "RESIF Data Centre",
#         "summary": "French seismologic and geodetic network",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "http://seismology.resif.fr/",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://ws.resif.fr/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://ws.resif.fr/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://ws.resif.fr/eidaws/wfcatalog/1/"
# }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "INGV",
#         "website": "http://www.ingv.it",
#         "fullName": "INGV Data Centre",
#         "summary": "Istituto Nazionale di Geofisica e Vulcanologia",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "http://www.ingv.it/",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://webservices.ingv.it/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://webservices.ingv.it/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://webservices.ingv.it/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "ETH",
#         "website": "https://www.ethz.ch",
#         "fullName": "ETH Data Centre",
#         "summary": u"Eidgenössische Technische Hochschule Zürich",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "http://www.seismo.ethz.ch/",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://eida.ethz.ch/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://eida.ethz.ch/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://eida.ethz.ch/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "BGR",
#         "website": "https://www.bgr.bund.de",
#         "fullName": "BGR Data Centre",
#         "summary": u"Bundesanstalt für Geowissenschaften und Rohstoffe",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "https://www.bgr.bund.de/EN/Themen/Seismologie",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://eida.bgr.de/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://eida.bgr.de/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://eida.bgr.de/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "NIEP",
#         "website": "http://www.infp.ro",
#         "fullName": "NIEP Data Centre",
#         "summary": "National Institute for Earth Physics",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "http://www.infp.ro",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://eida-sc3.infp.ro/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://eida-sc3.infp.ro/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://eida-sc3.infp.ro/eidaws/wfcatalog/1/ "
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "KOERI",
#         "website": "http://www.koeri.boun.edu.tr",
#         "fullName": "KOERI Data Centre",
#         "summary": "Kandilli Observatory and Earthquake Research Institute",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "http://www.koeri.boun.edu.tr/sismo/2/en/",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://eida-service.koeri.boun.edu.tr/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://eida-service.koeri.boun.edu.tr/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://eida-service.koeri.boun.edu.tr/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "LMU",
#         "website": "https://www.uni-muenchen.de/",
#         "fullName": "LMU Data Centre",
#         "summary": u"Ludwig Maximilians Universität München",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "https://www.geophysik.uni-muenchen.de/",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://erde.geophysik.uni-muenchen.de/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://erde.geophysik.uni-muenchen.de/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://erde.geophysik.uni-muenchen.de/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "NOA",
#         "website": "http://www.noa.gr",
#         "fullName": "NOA Data Centre",
#         "summary": "National Observatory of Athens",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "http://bbnet.gein.noa.gr",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://eida.gein.noa.gr/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://eida.gein.noa.gr/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://eida.gein.noa.gr/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "UIB",
#         "website": "https://www.uib.no/geo",
#         "fullName": "University of Bergen",
#         "summary": "Department of Earth Science - UiB",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "http://eida.geo.uib.no",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://eida.geo.uib.no/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://eida.geo.uib.no/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://eida.geo.uib.no/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     },
#     {
#         "name": "ICGC",
#         "website": "https://www.icgc.cat/",
#         "fullName": "Institut Cartogràfic i Geològic de Catalunya",
#         "summary": "Institut Cartogràfic i Geològic de Catalunya",
#         "repositories": [
#             {
#                 "name": "archive",
#                 "description": "Archive of continuous seismological data",
#                 "website": "http://icgc.cat",
#                 "services": [
#                     {
#                         "name": "fdsnws-dataselect-1",
#                         "description": "Access to raw time series data",
#                         "url": "http://ws.icgc.cat/fdsnws/dataselect/1/"
#                     },
#                     {
#                         "name": "fdsnws-station-1",
#                         "description": "Access to metadata describing raw time series data",
#                         "url": "http://ws.icgc.cat/fdsnws/station/1/"
#                     },
#                     {
#                         "name": "eidaws-wfcatalog",
#                         "description": "EIDA WFCatalog service",
#                         "url": "http://ws.icgc.cat/eidaws/wfcatalog/1/"
#                     }
#                 ],
#                 "datasets": [
#                 ]
#             }
#         ]
#     }
# ]


class FDSNRules(dict):
    """Based on a dict, but all functionality is in the datacentres list
     which groups data from many requests by datacenter.

    :platform: Any

    """

    # __slots__ = ()

    def __init__(self, rm=None, eidaDCs=None):
        super().__init__()
        self['version'] = 1
        self['datacenters'] = list()

        self.eidaDCs = eidaDCs
        if rm is None:
            return

        if type(rm) == type(RequestMerge()):
            for r in rm:
                for p in r['params']:
                    self.append(r['name'], r['url'], p['priority'],
                                Stream(p['net'], p['sta'], p['loc'], p['cha']),
                                TW(p['start'], p['end']))
            return

        raise Exception('FDSNRules cannot be created with an object different than RequestMerge.')

    def index(self, service, url):
        """Given a service and url returns the index on the list where
         the routes/rules should be added. If the data centre is still
         not in the list returns a KeyError with an index to the eidaDCs
         list. That is the DC to add. If both searches fail an Exception
         is raised"""

        service = 'fdsnws-availability-1' if service == 'availability' else service
        service = 'fdsnws-dataselect-1' if service == 'dataselect' else service
        service = 'fdsnws-station-1' if service == 'station' else service
        service = 'eidaws-wfcatalog' if service == 'wfcatalog' else service

        for inddc, dc in enumerate(self['datacenters']):
            for indrepo, repo in enumerate(dc['repositories']):
                for inddcservice, dcservice in enumerate(repo['services']):
                    if ((service == dcservice['name']) and
                            (url.startswith(dcservice['url']))):
                        return inddc

        # After the for...else variable indList points to the DC in this object
        for inddc, dc in enumerate(self.eidaDCs):
            for indrepo, repo in enumerate(dc['repositories']):
                for inddcservice, dcservice in enumerate(repo['services']):
                    if ((service == dcservice['name']) and
                            (url.startswith(dcservice['url']))):
                        raise KeyError(inddc)

        raise Exception('Data centre not found! (%s, %s)' % (service, url))

    def append(self, service, url, priority, stream, tw):
        """Append a new :class:`~Route` without repeating the datacenter.

        Overrides the *append* method of the inherited list. If another route
        for the datacenter was already added, the remaining attributes are
        appended in *datasets* for the datacenter. If this is the first
        :class:`~Route` for the datacenter, everything is added.

        :param service: Service name (f.i., 'dataselect')
        :type service: str
        :param url: URL for the service (f.i., 'http://server/path/query')
        :type url: str
        :param priority: Priority of the Route (1: highest priority)
        :type priority: int
        :param stream: Stream(s) associated with the Route
        :type stream: :class:`~Stream`
        :param tw: Start date for the Route
        :type tw: :class:`~TW`

        """

        # print(service, url, priority, stream, tw)
        url = url[:-len('query')] if url.endswith('query') else url
        service = 'fdsnws-%s-1' % service if service in ('station', 'dataselect', 'availability') else service
        service = 'eidaws-%s' % service if service in ('wfcatalog') else service

        # Include only mandatory attributes
        toAdd = {
            "priority": priority,
            "starttime": tw.start
        }

        # Add attributes with values different than the default ones
        if stream.n != '*' and len(stream.n):
            toAdd["network"] = stream.n
        if stream.s != '*' and len(stream.s):
            toAdd["station"] = stream.s
        if stream.l != '*' and len(stream.l):
            toAdd["location"] = stream.l
        if stream.c != '*' and len(stream.c):
            toAdd["channel"] = stream.c
        if tw.end is not None:
            if isinstance(tw.end, str) and len(tw.end):
                toAdd["endtime"] = tw.end
            if isinstance(tw.end, datetime.datetime):
                toAdd["endtime"] = tw.end

        # Search in which data centre should this be added
        try:
            indList = self.index(service, url)
        except KeyError as k:
            indList = len(self['datacenters'])
            self['datacenters'].append(deepcopy(self.eidaDCs[k.args[0]]))

            # This is empty and then it can be already added
            # toAdd["services"] = [service]
        except Exception:
            return

        toAdd["services"] = [{"name": service, "url": url}]

        # print(self['datacenters'][indList]['repositories'][0]['datasets'])
        tsrIndex = 0
        # FIXME the position in repositories is hard-coded!
        # Check if the request line had been already added
        for ind, srvDC in enumerate(self['datacenters'][indList]['repositories'][0]['datasets']):
            if not (toAdd.get("network", '*') == srvDC.get("network", '*')):
                continue
            if not (toAdd.get("station", '*') == srvDC.get("station", '*')):
                continue
            if not (toAdd.get("location", '*') == srvDC.get("location", '*')):
                continue
            if not (toAdd.get("channel", '*') == srvDC.get("channel", '*')):
                continue
            if not (toAdd.get("starttime", None) == srvDC.get("starttime", None)):
                continue
            if not (toAdd.get("endtime", None) == srvDC.get("endtime", None)):
                continue
            if not (toAdd.get("priority", None) == srvDC.get("priority", None)):
                continue
            # print('Agregar', toAdd, 'to', srvDC)
            srvDC["services"].append({"name": service, "url": url})
            tsrIndex = ind
            break
        else:
            tsrIndex = len(self['datacenters'][indList]['repositories'][0]['datasets'])
            self['datacenters'][indList]['repositories'][0]['datasets'].append(toAdd)

        # Check that there is the same number of routes for datasets and services
        if len(self['datacenters'][indList]['repositories'][0]['datasets'][tsrIndex]['services']) != \
                len(self['datacenters'][indList]['repositories'][0]['services']):
            return

        # Check that each datasets is in ['services']
        tsr = self['datacenters'][indList]['repositories'][0]['datasets'][tsrIndex]

        svcset = set()
        for dcservice in self['datacenters'][indList]['repositories'][0]['services']:
            svcset.add((dcservice['name'], dcservice['url']))

        for svc in tsr['services']:
            # print(svc)
            try:
                svcset.remove((svc['name'], svc['url']))
            except KeyError:
                return

        # Remove all datasets because it is the same as services
        del self['datacenters'][indList]['repositories'][0]['datasets'][tsrIndex]['services']

    def extend(self, listReqM):
        """Append all the items in :class:`~RequestMerge` grouped by datacenter.

        Overrides the *extend* method of the inherited list. If another route
        for the datacenter was already added, the remaining attributes are
        appended in *params* for the datacenter. If this is the first
        :class:`~Route` for the datacenter, everything is added.

        :param listReqM: Requests from (possibly) different datacenters to be
            added
        :type listReqM: list of :class:`~RequestMerge`

        """
        # FIXME Re-implement this!!!
        for r in listReqM:
            try:
                pos = self.index(r['name'], r['url'])
                self['datacenters'][pos]['params'].extend(r['params'])
            except:
                self['datacenters'].append(r)


def str2date(dStr):
    """Transform a string to a datetime.

    :param dStr: A datetime in ISO format.
    :type dStr: string
    :return: A datetime represented the converted input.
    :rtype: datetime
    """
    # In case of empty string
    if not len(dStr):
        return None

    dateParts = dStr.replace('-', ' ').replace('T', ' ')
    dateParts = dateParts.replace(':', ' ').replace('.', ' ')
    dateParts = dateParts.replace('Z', '').split()
    return datetime.datetime(*map(int, dateParts))


def checkOverlap(str1, routeList, str2, route):
    """Check overlap of routes from stream str1 and a route from str2.

    :param str1: First stream
    :type str1: Stream
    :param routeList: List of routes already present
    :type routeList: list
    :param str2: Second stream
    :type str2: Stream
    :param route: Route to be checked
    :type route: Route
    :rtype: boolean
    :returns: Value indicating if routes overlap for both streams
    """
    if str1.overlap(str2):
        for auxRoute in routeList:
            if auxRoute.overlap(route):
                return True

    return False


def getStationCache(st, rt):
    """Retrieve station name and location from a particular station service.

    :param st: Stream for which a cache should be saved.
    :type st: Stream
    :param rt: Route where this stream is archived.
    :type rt: Route
    :returns: Stations found in this route for this stream pattern.
    :rtype: list
    """
    query = '%s?format=text&net=%s&sta=%s&start=%s' % \
            (rt.address, st.n, st.s, rt.tw.start.isoformat())
    if rt.tw.end is not None:
        query = query + '&end=%s' % rt.tw.end.isoformat()

    logging.debug(query)

    # FIXME INGV must fix their firewall rules!
    if 'ingv.it' in query:
        sleep(1)

    req = ul.Request(query)
    try:
        u = ul.urlopen(req, timeout=15)
        # What is read has to be decoded in python3
        buf = u.read().decode('utf-8')
    except URLError as e:
        logging.warning('The URL does not seem to be a valid Station-WS')
        if hasattr(e, 'reason'):
            logging.warning('%s - Reason: %s\n' % (rt.address, e.reason))
        elif hasattr(e, 'code'):
            logging.warning('The server couldn\'t fulfill the request.')
            logging.warning('Error code: %s\n', e.code)
        return list()
    except Exception as e:
        logging.warning('WATCH THIS! %s' % e)
        return list()

    result = list()
    for line in buf.splitlines():
        if line.startswith('#'):
            continue
        lSplit = line.split('|')
        try:
            start = str2date(lSplit[6])
            endt = str2date(lSplit[7])
            result.append(Station(lSplit[1], float(lSplit[2]),
                          float(lSplit[3]), start, endt))
        except Exception:
            logging.error('Error trying to add station: (%s, %s, %s, %s, %s)' %
                          (lSplit[1], lSplit[2], lSplit[3], lSplit[6],
                           lSplit[7]))
    # print(result)
    if not len(result):
        logging.warning('No stations found for streams %s in %s' %
                        (st, rt.address))
    return result


def cacheStations(routingTable, stationTable):
    """Loop for all station-WS and cache all station names and locations.

    :param routingTable: Routing table.
    :type routingTable: dict
    :param stationTable: Cache with names and locations of stations.
    :type stationTable: dict
    """
    ptRT = routingTable
    for st in ptRT.keys():
        # Set a default result
        result = None

        # Set with the domain from all routes related to this stream
        services = set(urlparse(rt.address).netloc for rt in ptRT[st])
        for rt in ptRT[st]:
            if rt.service == 'station':
                if result is None:
                    result = getStationCache(st, rt)
                else:
                    result.extend(getStationCache(st, rt))

        if result is None:
            logging.warning('No Station-WS defined for this stream! No cache!')
            # Set a default value so that things still work
            result = list()

        for service in services:
            try:
                stationTable[service][st] = result
            except KeyError:
                stationTable[service] = dict()
                stationTable[service][st] = result


def addVirtualNets(fileName, **kwargs):
    """Read the routing file in XML format and store its VNs in memory.

    All information related to virtual networks is read into a dictionary. Only
    the necessary attributes are stored. This relies on the idea
    that some other agent should update the routing file at
    regular periods of time.

    :param fileName: File with virtual networks to add to the routing table.
    :type fileName: str
    :param **kwargs: See below
    :returns: Updated table containing aliases from the input file.
    :rtype: dict

    :Keyword Arguments:
        * *vnTable* (``dict``) Table with virtual networks where aliases should be added.
    """
    # VN table is empty (default)
    ptVN = kwargs.get('vnTable', dict())

    logs = logging.getLogger('addVirtualNets')
    logs.debug('Entering addVirtualNets()\n')

    try:
        vnHandle = open(fileName, 'r', encoding='utf-8')
    except Exception:
        msg = 'Error: %s could not be opened.\n'
        logs.error(msg % fileName)
        return ptVN

    # Traverse through the virtual networks
    # get an iterable
    try:
        context = ET.iterparse(vnHandle, events=("start", "end"))
    except IOError as e:
        logs.error(str(e))
        return ptVN

    # turn it into an iterator
    context = iter(context)

    # get the root element
    if hasattr(context, 'next'):
        event, root = context.next()
    else:
        event, root = next(context)

    # Check that it is really an inventory
    if root.tag[-len('routing'):] != 'routing':
        msg = 'The file parsed seems not to be a routing file (XML).\n'
        logs.error(msg)
        return ptVN

    # Extract the namespace from the root node
    namesp = root.tag[:-len('routing')]

    for event, vnet in context:
        # The tag of this node should be "route".
        # Now it is not being checked because
        # we need all the data, but if we need to filter, this
        # is the place.
        #
        if event == "end":
            if vnet.tag == namesp + 'vnetwork':

                # Extract the network code
                try:
                    vnCode = vnet.get('networkCode')
                    if len(vnCode) == 0:
                        vnCode = None
                except Exception:
                    vnCode = None

                # Traverse through the sources
                # for arcl in route.findall(namesp + 'dataselect'):
                for stream in vnet:
                    # Extract the networkCode
                    msg = 'Only the * wildcard is allowed in virtual nets.'
                    try:
                        net = stream.get('networkCode')
                        if (('?' in net) or
                                (('*' in net) and (len(net) > 1))):
                            logs.warning(msg)
                            continue
                    except Exception:
                        net = '*'

                    # Extract the stationCode
                    try:
                        sta = stream.get('stationCode')
                        if (('?' in sta) or
                                (('*' in sta) and (len(sta) > 1))):
                            logs.warning(msg)
                            continue
                    except Exception:
                        sta = '*'

                    # Extract the locationCode
                    try:
                        loc = stream.get('locationCode')
                        if (('?' in loc) or
                                (('*' in loc) and (len(loc) > 1))):
                            logs.warning(msg)
                            continue
                    except Exception:
                        loc = '*'

                    # Extract the streamCode
                    try:
                        cha = stream.get('streamCode')
                        if (('?' in cha) or
                                (('*' in cha) and (len(cha) > 1))):
                            logs.warning(msg)
                            continue
                    except Exception:
                        cha = '*'

                    try:
                        auxStart = stream.get('start')
                        startD = str2date(auxStart)
                    except Exception:
                        startD = None
                        msg = 'Error while converting START attribute.\n'
                        logs.warning(msg)

                    try:
                        auxEnd = stream.get('end')
                        endD = str2date(auxEnd)
                    except Exception:
                        endD = None
                        msg = 'Error while converting END attribute.\n'
                        logs.warning(msg)

                    if vnCode not in ptVN:
                        ptVN[vnCode] = [(Stream(net, sta, loc, cha),
                                         TW(startD, endD))]
                    else:
                        ptVN[vnCode].append((Stream(net, sta, loc, cha),
                                             TW(startD, endD)))

                    stream.clear()

                vnet.clear()

            # FIXME Probably the indentation below is wrong.
            root.clear()

    return ptVN


def addRoutes(fileName, **kwargs):
    """Read the routing file in XML format and store it in memory.

    All the routing information is read into a dictionary. Only the
    necessary attributes are stored. This relies on the idea
    that some other agent should update the routing file at
    regular periods of time.

    :param fileName: File with routes to add the the routing table.
    :type fileName: str
    :param **kwargs: See below
    :returns: Updated routing table containing routes from the input file.
    :rtype: dict

    :Keyword Arguments:
        * *routingTable* (``dict``) Routing Table where routes should be added to.
    """
    # Routing table is empty (default)
    ptRT = kwargs.get('routingTable', dict())

    logs = logging.getLogger('addRoutes')
    logs.debug('Entering addRoutes(%s)\n' % fileName)

    # Default value is NOT to allow overlapping streams
    allowOverlaps = kwargs.get('allowOverlaps', False)

    logs.info('Overlaps between routes will ' +
              ('' if allowOverlaps else 'NOT ' + 'be allowed'))

    with open(fileName, 'r', encoding='utf-8') as testFile:
        # Parse the routing file
        # Traverse through the networks
        # get an iterable
        try:
            context = ET.iterparse(testFile, events=("start", "end"))
        except IOError:
            msg = 'Error: %s could not be parsed. Skipping it!\n' % fileName
            logs.error(msg)
            return ptRT

        # turn it into an iterator
        context = iter(context)

        try:  
            # get the root element
            # More Python 3 compatibility
            if hasattr(context, 'next'):
                event, root = context.next()
            else:
                event, root = next(context)
        except Exception:
            msg = 'Error: %s could not be parsed. Reading backup!\n' % fileName
            logs.error(msg)
            testFile.close()
            os.rename(fileName, fileName + '.wrong')
            try:
                os.rename(fileName + '.bck', fileName)
                testFile = open(fileName, 'r', encoding='utf-8')
                context = ET.iterparse(testFile, events=("start", "end"))
                context = iter(context)
                # get the root element
                # More Python 3 compatibility
                if hasattr(context, 'next'):
                    event, root = context.next()
                else:
                    event, root = next(context)
            except Exception:
                return ptRT
            
        # Check that it is really an inventory
        if root.tag[-len('routing'):] != 'routing':
            msg = '%s seems not to be a routing file (XML). Skipping it!\n' \
                % fileName
            logs.error(msg)
            return ptRT

        # Extract the namespace from the root node
        namesp = root.tag[:-len('routing')]

        for event, route in context:
            # The tag of this node should be "route".
            # Now it is not being checked because
            # we need all the data, but if we need to filter, this
            # is the place.
            #
            if event == "end":
                if route.tag == namesp + 'route':

                    # Extract the location code
                    try:
                        locationCode = route.get('locationCode')
                        if len(locationCode) == 0:
                            locationCode = '*'

                        # Do not allow "?" wildcard in the input, because it
                        # will be impossible to match with the user input if
                        # this also has a mixture of "*" and "?"
                        if '?' in locationCode:
                            logs.error('Wildcard "?" is not allowed!')
                            continue

                    except Exception:
                        locationCode = '*'

                    # Extract the network code
                    try:
                        networkCode = route.get('networkCode')
                        if len(networkCode) == 0:
                            networkCode = '*'

                        # Do not allow "?" wildcard in the input, because it
                        # will be impossible to match with the user input if
                        # this also has a mixture of "*" and "?"
                        if '?' in networkCode:
                            logs.error('Wildcard "?" is not allowed!')
                            continue

                    except Exception:
                        networkCode = '*'

                    # Extract the station code
                    try:
                        stationCode = route.get('stationCode')
                        if len(stationCode) == 0:
                            stationCode = '*'

                        # Do not allow "?" wildcard in the input, because it
                        # will be impossible to match with the user input if
                        # this also has a mixture of "*" and "?"
                        if '?' in stationCode:
                            logs.error('Wildcard "?" is not allowed!')
                            continue

                    except Exception:
                        stationCode = '*'

                    # Extract the stream code
                    try:
                        streamCode = route.get('streamCode')
                        if len(streamCode) == 0:
                            streamCode = '*'

                        # Do not allow "?" wildcard in the input, because it
                        # will be impossible to match with the user input if
                        # this also has a mixture of "*" and "?"
                        if '?' in streamCode:
                            logs.error('Wildcard "?" is not allowed!')
                            continue

                    except Exception:
                        streamCode = '*'

                    # Traverse through the sources
                    for serv in route:
                        assert serv.tag[:len(namesp)] == namesp

                        service = serv.tag[len(namesp):]
                        att = serv.attrib

                        # Extract the address (mandatory)
                        try:
                            address = att.get('address')
                            if len(address) == 0:
                                logs.error('Could not add %s' % att)
                                continue
                        except Exception:
                            logs.error('Could not add %s' % att)
                            continue

                        try:
                            auxStart = att.get('start', None)
                            startD = str2date(auxStart)
                        except Exception:
                            startD = None

                        # Extract the end datetime
                        try:
                            auxEnd = att.get('end', None)
                            endD = str2date(auxEnd)
                        except Exception:
                            endD = None

                        # Extract the priority
                        try:
                            priority = att.get('priority', '99')
                            if len(priority) == 0:
                                priority = 99
                            else:
                                priority = int(priority)
                        except Exception:
                            priority = 99

                        # Append the network to the list of networks
                        st = Stream(networkCode, stationCode, locationCode,
                                    streamCode)
                        tw = TW(startD, endD)
                        rt = Route(service, address, tw, priority)

                        try:
                            # Check the overlap between the routes to import
                            # and the ones already present in the main Routing
                            # table
                            addIt = True
                            logs.debug('[RT] Checking %s' % str(st))
                            for testStr in ptRT.keys():
                                # This checks the overlap of Streams and also
                                # of timewindows and priority
                                if checkOverlap(testStr, ptRT[testStr], st,
                                                rt):
                                    msg = '%s: Overlap between %s and %s!\n'\
                                        % (fileName, st, testStr)
                                    logs.error(msg)
                                    if not allowOverlaps:
                                        logs.error('Skipping %s\n' % str(st))
                                        addIt = False
                                    break

                            if addIt:
                                ptRT[st].append(rt)
                            else:
                                logs.warning('Skip %s - %s\n' % (st, rt))

                        except KeyError:
                            ptRT[st] = [rt]
                        serv.clear()

                    route.clear()

                root.clear()

    # Order the routes by priority
    for keyDict in ptRT:
        ptRT[keyDict] = sorted(ptRT[keyDict])

    return ptRT


def replacelast(s, old, new):
    return (s[::-1].replace(old[::-1], new[::-1], 1))[::-1]


# FIXME It is probably better to swap the first two parameters
def addRemote(fileName, url, method='localconfig'):
    """Read the routing file from a remote datacenter and store it in memory.

    All the routing information is read into a dictionary. Only the
    necessary attributes are stored.

    :param fileName: file where the routes should be saved
    :type fileName: str
    :param url: Base URL from the Routing Service at the remote datacenter
    :type url: str
    :param method: Method from the remote RS to be called
    :type method: str
    :raise: Exception

    """
    logs = logging.getLogger('addRemote')
    logs.debug('Entering addRemote(%s)\n' % os.path.basename(fileName))

    blockSize = 4096 * 100

    fileName = fileName + '.download'

    try:
        os.remove(fileName)
        logs.debug('Successfully removed %s\n' % fileName)
    except Exception:
        pass

    # Connect to the proper Routing-WS
    try:
        if url.startswith('http://') or url.startswith('https://'):
            # Prepare Request
            req = ul.Request(url + '/%s' % method)
            u = ul.urlopen(req)
        else:
            u = open(url, 'r')

        with open(fileName, 'w', encoding='utf-8') as routeExt:
            logs.debug('%s opened\n%s:' % (fileName, url))
            # Read the data in blocks of predefined size
            buf = u.read(blockSize)
            if isinstance(buf, bytes):
                buf = buf.decode('utf-8')
            while len(buf):
                logs.debug('.')
                # Return one block of data
                routeExt.write(buf)
                buf = u.read(blockSize)
                if isinstance(buf, bytes):
                    buf = buf.decode('utf-8')

            # Close the connection to avoid overloading the server
            u.close()

    except URLError as e:
        logs.warning('The URL does not seem to be a valid Routing Service')
        if hasattr(e, 'reason'):
            logs.warning('%s/%s - Reason: %s\n' % (url, method, e.reason))
        elif hasattr(e, 'code'):
            logs.warning('The server couldn\'t fulfill the request.')
            logs.warning('Error code: %s\n', e.code)
        logs.warning('Retrying with a static configuration file')

        # TODO Think a way to do this better
        if method == 'dc':
            url = replacelast(url, '.xml', '.json')

        # Prepare Request without the "localconfig" method
        req = ul.Request(url)
        try:
            u = ul.urlopen(req)

            with open(fileName, 'w', encoding='utf-8') as routeExt:
                logs.debug('%s opened\n%s:' % (fileName, url))
                # Read the data in blocks of predefined size
                buf = u.read(blockSize).decode('utf-8')
                while len(buf):
                    logs.debug('.')
                    # Return one block of data
                    routeExt.write(buf)
                    buf = u.read(blockSize).decode('utf-8')

                # Close the connection to avoid overloading the server
                u.close()
        except URLError as e:
            if hasattr(e, 'reason'):
                logs.error('%s - Reason: %s\n' % (url, e.reason))
            elif hasattr(e, 'code'):
                logs.error('The server couldn\'t fulfill the request.')
                logs.error('Error code: %s\n', e.code)
            # I have to return because there is no data. Otherwise, the old
            # data will be removed (see below).
            return

    name = fileName[:- len('.download')]
    try:
        os.remove(name + '.bck')
        logs.debug('Successfully removed %s\n' % (name + '.bck'))
    except Exception:
        pass

    try:
        os.rename(name, name + '.bck')
        logs.debug('Successfully renamed %s to %s.bck\n' % (name, name))
    except Exception:
        pass

    try:
        os.rename(fileName, name)
        logs.debug('Successfully renamed %s to %s\n' % (fileName, name))
    except Exception:
        raise Exception('Could not create the final version of %s.xml' %
                        os.path.basename(fileName))


class RequestMerge(list):
    """Extend a list to group data from many requests by datacenter.

    :platform: Any

    """

    __slots__ = ()

    def append(self, service, url, priority, stream, tw):
        """Append a new :class:`~Route` without repeating the datacenter.

        Overrides the *append* method of the inherited list. If another route
        for the datacenter was already added, the remaining attributes are
        appended in *params* for the datacenter. If this is the first
        :class:`~Route` for the datacenter, everything is added.

        :param service: Service name (f.i., 'dataselect')
        :type service: str
        :param url: URL for the service (f.i., 'http://server/path/query')
        :type url: str
        :param priority: Priority of the Route (1: highest priority)
        :type priority: int
        :param stream: Stream(s) associated with the Route
        :type stream: :class:`~Stream`
        :param tw: Time window for the Route
        :type tw: :class:`~TW`

        """
        try:
            pos = self.index(service, url)
            self[pos]['params'].append({'net': stream.n, 'sta': stream.s,
                                        'loc': stream.l, 'cha': stream.c,
                                        'start': tw.start, 'end': tw.end,
                                        'priority': priority if priority
                                        is not None else ''})
        except Exception:
            # Take a reference to the inherited *list* and do a normal append
            listPar = super(RequestMerge, self)

            listPar.append({'name': service, 'url': url,
                            'params': [{'net': stream.n, 'sta': stream.s,
                                        'loc': stream.l, 'cha': stream.c,
                                        'start': tw.start, 'end': tw.end,
                                        'priority': priority if priority
                                        is not None else ''}]})

    def index(self, service, url):
        """Check for the service and url specified in the parameters.

        This overrides the *index* method of the inherited list.

        :param service: Requests from (possibly) different datacenters to be
            added
        :type service: str
        :param url: Address of the service provided by a datacenter
        :type url: str
        :returns: position in the list where the service and url specified can
            be found
        :rtype: int
        :raises: ValueError

        """
        for ind, r in enumerate(self):
            if (r['name'] == service) and (r['url'] == url):
                return ind

        raise ValueError()

    def extend(self, listReqM):
        """Append all the items in :class:`~RequestMerge` grouped by datacenter.

        Overrides the *extend* method of the inherited list. If another route
        for the datacenter was already added, the remaining attributes are
        appended in *params* for the datacenter. If this is the first
        :class:`~Route` for the datacenter, everything is added.

        :param listReqM: Requests from (posibly) different datacenters to be
            added
        :type listReqM: list of :class:`~RequestMerge`

        """
        for r in listReqM:
            try:
                pos = self.index(r['name'], r['url'])
                self[pos]['params'].extend(r['params'])
            except Exception:
                super(RequestMerge, self).append(r)


class Station(namedtuple('Station', ['name', 'latitude', 'longitude', 'start', 'end'])):
    """Namedtuple representing a Station.

    This is the minimum information which needs to be cached from a station in
    order to be able to apply a proper filter to the inventory when queries
    f.i. do not include the network name.
           name: station name
           latitude: latitude
           longitude: longitude

    :platform: Any

    """

    __slots__ = ()


class geoRectangle(namedtuple('geoRectangle', ['minlat', 'maxlat', 'minlon', 'maxlon'])):
    """Namedtuple representing a geographical rectangle.

           minlat: minimum latitude
           maxlat: maximum latitude
           minlon: minimum longitude
           maxlon: maximum longitude

    :platform: Any

    """

    __slots__ = ()

    def contains(self, lat, lon):
        """Check if the point belongs to the rectangle."""
        return True if ((self.minlat <= lat <= self.maxlat) and
                        (self.minlon <= lon <= self.maxlon)) else False


class Stream(namedtuple('Stream', ['n', 's', 'l', 'c'])):
    """Namedtuple representing a Stream.

    It includes methods to calculate matching and overlapping of streams
    including (or not) wildcards. Components are the usual to determine a
    stream:
           n: network
           s: station
           l: location
           c: channel

    :platform: Any

    """

    __slots__ = ()

    def toXMLopen(self, nameSpace='ns0', level=1):
        """Export the stream to XML representing a route.

        XML representation is incomplete and needs to be closed by the method
        toXMLclose.

        """
        conv = '%s<%s:route networkCode="%s" stationCode="%s" ' + \
            'locationCode="%s" streamCode="%s">\n'
        return conv % (' ' * level, nameSpace, self.n, self.s, self.l, self.c)

    def toXMLclose(self, nameSpace='ns0', level=1):
        """Close the XML representation of a route given by toXMLopen."""
        return '%s</%s:route>\n' % (' ' * level, nameSpace)

    def __contains__(self, st):
        """Check if one :class:`~Stream` is contained in this :class:`~Stream`.

        :param st: :class:`~Stream` which should checked for overlapping
        :type st: :class:`~Stream`
        :returns: Value specifying whether the given stream is contained in
            this one
        :rtype: Bool

        """
        if (fnmatch.fnmatch(st.n, self.n) and
                fnmatch.fnmatch(st.s, self.s) and
                fnmatch.fnmatch(st.l, self.l) and
                fnmatch.fnmatch(st.c, self.c)):
            return True

        return False

    def strictMatch(self, other):
        """Return a *reduction* of this stream to match what's been received.

        :param other: :class:`~Stream` which should be checked for overlaps
        :type other: :class:`~Stream`
        :returns: *reduced* version of this :class:`~Stream` to match the one
            passed in the parameter
        :rtype: :class:`~Stream`
        :raises: Exception

        """
        res = list()
        for i in range(len(other)):
            if (self[i] is None) or (fnmatch.fnmatch(other[i], self[i])):
                res.append(other[i])
            elif (other[i] is None) or (fnmatch.fnmatch(self[i], other[i])):
                res.append(self[i])
            else:
                raise Exception('No overlap or match between streams.')

        return Stream(*tuple(res))

    def overlap(self, other):
        """Check if there is an overlap between this stream and other one.

        :param other: :class:`~Stream` which should be checked for overlaps
        :type other: :class:`~Stream`
        :returns: Value specifying whether there is an overlap between this
                  stream and the one passed as a parameter
        :rtype: Bool

        """
        for i in range(len(other)):
            if ((self[i] is not None) and (other[i] is not None) and
                    not fnmatch.fnmatch(self[i], other[i]) and
                    not fnmatch.fnmatch(other[i], self[i])):
                return False
        return True


class TW(namedtuple('TW', ['start', 'end'])):
    """Namedtuple with methods to perform calculations on timewindows.

    Attributes are:
           start: Start datetime
           end: End datetime

    :platform: Any

    """

    __slots__ = ()

    # This method works with the "in" clause or with the "overlap" method
    def __contains__(self, otherTW):
        """Wrap of the overlap method to allow  the use of the "in" clause.

        :param otherTW: timewindow which should be checked for overlaps
        :type otherTW: :class:`~TW`
        :returns: Value specifying whether there is an overlap between this
            timewindow and the one in the parameter
        :rtype: Bool

        """
        return self.overlap(otherTW)

    def overlap(self, otherTW):
        """Check if the otherTW is contained in this :class:`~TW`.

        :param otherTW: timewindow which should be checked for overlapping
        :type otherTW: :class:`~TW`
        :returns: Value specifying whether there is an overlap between this
                  timewindow and the one in the parameter
        :rtype: Bool

        .. rubric:: Examples

        >>> y2011 = datetime.datetime(2011, 1, 1)
        >>> y2012 = datetime.datetime(2012, 1, 1)
        >>> y2013 = datetime.datetime(2013, 1, 1)
        >>> y2014 = datetime.datetime(2014, 1, 1)
        >>> TW(y2011, y2014).overlap(TW(y2012, y2013))
        True
        >>> TW(y2012, y2014).overlap(TW(y2011, y2013))
        True
        >>> TW(y2012, y2013).overlap(TW(y2011, y2014))
        True
        >>> TW(y2011, y2012).overlap(TW(y2013, y2014))
        False

        """
        def inOrder(a, b, c):
            if ((b is None) and (a is not None) and (c is not None)):
                return False

            # Here I'm sure that b is not None
            if (a is None and c is None):
                return True

            # Here I'm sure that b is not None
            if (b is None and c is None):
                return True

            # I also know that a or c are not None
            if a is None:
                return b < c

            if c is None:
                return a < b

            # The three are not None
            # print a, b, c, a < b, b < c, a < b < c
            return a < b < c

        def inOrder2(a, b, c):
            # The three are not None
            # print a, b, c, a < b, b < c, a < b < c
            return a <= b <= c

        # First of all check that the TWs are correctly created
        if ((self.start is not None) and (self.end is not None) and
                (self.start > self.end)):
            raise ValueError('Start greater than End: %s > %s' % (self.start,
                                                                  self.end))

        if ((otherTW.start is not None) and (otherTW.end is not None) and
                (otherTW.start > otherTW.end)):
            raise ValueError('Start greater than End %s > %s' % (otherTW.start,
                                                                 otherTW.end))

        minDT = datetime.datetime(1900, 1, 1)
        maxDT = datetime.datetime(3000, 1, 1)

        sStart = self.start if self.start is not None else minDT
        oStart = otherTW.start if otherTW.start is not None else minDT
        sEnd = self.end if self.end is not None else maxDT
        oEnd = otherTW.end if otherTW.end is not None else maxDT

        if inOrder2(oStart, sStart, oEnd) or \
                inOrder2(oStart, sEnd, oEnd):
            return True

        # Check if this is included in otherTW
        if inOrder2(oStart, sStart, sEnd):
            return inOrder2(sStart, sEnd, oEnd)

        # Check if otherTW is included in this one
        if inOrder2(sStart, oStart, oEnd):
            return inOrder2(oStart, oEnd, sEnd)

        if self == otherTW:
            return True

        raise Exception('TW.overlap unresolved %s:%s' % (self, otherTW))

    def difference(self, otherTW):
        """Substract otherTW from this TW.

        The result is a list of TW. This operation does not modify the data in
        the current timewindow.

        :param otherTW: timewindow which should be substracted from this one
        :type otherTW: :class:`~TW`
        :returns: Difference between this timewindow and the one in the
                  parameter
        :rtype: list of :class:`~TW`

        """
        result = []

        if otherTW.start is not None:
            if ((self.start is None and otherTW.start is not None) or
                    ((self.start is not None) and
                     (self.start < otherTW.start))):
                result.append(TW(self.start, otherTW.start))

        if otherTW.end is not None:
            if ((self.end is None and otherTW.end is not None) or
                    ((self.end is not None) and
                     (self.end > otherTW.end))):
                result.append(TW(otherTW.end, self.end))

        return result

    def intersection(self, otherTW):
        """Calculate the intersection between otherTW and this TW.

        This operation does not modify the data in the current timewindow.

        :param otherTW: timewindow which should be intersected with this one
        :type otherTW: :class:`~TW`
        :returns: Intersection between this timewindow and the one in the
                  parameter
        :rtype: :class:`~TW`

        """

        # Trivial case
        if otherTW.start is None and otherTW.end is None:
            return self

        if otherTW.start is not None:
            resSt = max(self.start, otherTW.start) if self.start is not None \
                else otherTW.start
        else:
            resSt = self.start

        if otherTW.end is not None:
            resEn = min(self.end, otherTW.end) if self.end is not None \
                else otherTW.end
        else:
            resEn = self.end

        if (resSt is not None) and (resEn is not None) and (resSt >= resEn):
            raise ValueError('Intersection is empty')

        return TW(resSt, resEn)


class Route(namedtuple('Route', ['service', 'address', 'tw', 'priority'])):
    """Namedtuple defining a :class:`~Route`.

    The attributes are
           service: service name
           address: a URL
           tw: timewindow
           priority: priority of the route

    :platform: Any

    """

    __slots__ = ()

    def toXML(self, nameSpace='ns0', level=2):
        """Export the Route to an XML representation."""
        return '%s<%s:%s address="%s" priority="%d" start="%s" end="%s" />\n' \
            % (' ' * level, nameSpace, self.service, self.address,
               self.priority, self.tw.start.isoformat()
               if self.tw.start is not None else '',
               self.tw.end.isoformat() if self.tw.end is not None else '')

    def overlap(self, otherRoute):
        """Check if there is an overlap between this route and otherRoute.

        :param otherRoute: :class:`~Route` which should be checked for overlaps
        :type otherRoute: :class:`~Route`
        :returns: Value specifying whether there is an overlap between this
                  stream and the one passed as a parameter
        :rtype: Bool

        """
        if ((self.priority == otherRoute.priority) and
                (self.service == otherRoute.service)):
            return self.tw.overlap(otherRoute.tw)
        return False

    def __contains__(self, pointTime):
        """DEPRECATED METHOD."""
        raise Exception('This should not be used! Switch to the TW method!')
        # if pointTime is None:
        #     return True

        # try:
        #     if (((self.tw.start is None) or (self.tw.start < pointTime)) and
        #             ((self.tw.end is None) or (pointTime < self.tw.end))):
        #         return True
        # except Exception:
        #     pass
        # return False


Route.__eq__ = lambda self, other: self.priority == other.priority
Route.__ne__ = lambda self, other: self.priority != other.priority
Route.__lt__ = lambda self, other: self.priority < other.priority
Route.__le__ = lambda self, other: self.priority <= other.priority
Route.__gt__ = lambda self, other: self.priority > other.priority
Route.__ge__ = lambda self, other: self.priority >= other.priority


class RoutingException(Exception):
    """Exception raised to flag a problem when searching for routes."""

    pass


# Define this just to shorten the notation
defRectangle = geoRectangle(-90, 90, -180, 180)


class RoutingCache(object):
    """Manage routing information of streams read from an Arclink-XML file.

    :platform: Linux (maybe also Windows)

    """

    def __init__(self, routingFile=None, config='routing.cfg'):
        """Constructor of RoutingCache.

        :param routingFile: XML file with routing information
        :type routingFile: str
        :param config: File where the configuration must be read from
        :type config: str

        """
        # Save the logging object
        self.logs = logging.getLogger('RoutingCache')

        # Arclink routing file in XML format
        self.routingFile = routingFile

        # Arclink routing file in XML format
        self.configFile = config

        # Dictionary with all the routes
        self.routingTable = dict()
        self.logs.info('Reading routes from %s' % self.routingFile)
        self.logs.info('Reading configuration from %s' % self.configFile)

        # Dictionary with list of stations inside each virtual network
        self.vnTable = dict()

        if self.routingFile is not None:
            self.logs.info('Wait until the RoutingCache is updated...')
            self.update()
            self.logs.info('RoutingCache finished!')

    def toXML(self, foutput, nameSpace='ns0'):
        """Export the RoutingCache to an XML representation."""
        header = """<?xml version="1.0" encoding="utf-8"?>
<ns0:routing xmlns:ns0="http://geofon.gfz-potsdam.de/ns/Routing/1.0/">
"""
        with open(foutput, 'w', encoding='utf-8') as fo:
            fo.write(header)
            for st, lr in self.routingTable.iteritems():
                fo.write(st.toXMLopen())
                for r in lr:
                    fo.write(r.toXML())
                fo.write(st.toXMLclose())
            fo.write('</ns0:routing>')

    def virtualNets(self):
        """Return the virtual networks defined in the system

        :returns: Virtual networks in this system in JSON format
        :rtype: str

        """
        return json.dumps(self.vnTable, default=datetime.datetime.isoformat)

    def localConfig(self, format='xml'):
        """Return the local routing configuration.

        :returns: Local routing information in Arclink-XML format
        :rtype: str

        """
        if format == 'xml':
            with open(self.routingFile) as f:
                return f.read()

        raise Exception('Format (%s) is not xml.' % format)

    def globalConfig(self, format='fdsn'):
        """Return the global routing configuration.

        :returns: Global routing information in FDSN format
        :rtype: str

        """
        if format == 'fdsn':
            result = self.getRoute(Stream('*', '*', '*', '*'), TW(None, None), service='dataselect,wfcatalog,station',
                                   alternative=True)
            fdsnresult = FDSNRules(result, self.eidaDCs)
            return json.dumps(fdsnresult, default=datetime.datetime.isoformat)

        raise Exception('Format (%s) is not fdsn.' % format)

    def getRoute(self, stream, tw, service='dataselect', geoLoc=None,
                 alternative=False):
        """Return routes to request data for the stream and timewindow provided.

        Based on a stream(s) and a timewindow returns all the needed
        information (URLs and parameters) to do the requests to different
        datacenters (if needed) and be able to merge the returned data avoiding
        duplication.

        :param stream: :class:`~Stream` definition including wildcards
        :type stream: :class:`~Stream`
        :param tw: Timewindow
        :type tw: :class:`~TW`
        :param service: Comma-separated list of services to get information from
        :type service: str
        :param geoLoc: Rectangle to filter stations
        :type geoLoc: :class:`~geoRectangle`
        :param alternative: Specifies whether alternative routes should be
            included
        :type alternative: bool
        :returns: URLs and parameters to request the data
        :rtype: :class:`~RequestMerge`
        :raises: RoutingException

        """
        # Convert from virtual network to real networks (if needed)
        strtwList = self.vn2real(stream, tw)
        self.logs.debug('Converting %s to %s' % (stream, strtwList))

        if not len(strtwList):
            msg = 'No routes found after resolving virtual network code.'
            raise RoutingException(msg)

        result = RequestMerge()
        for st, tw in strtwList:
            try:
                for srv in set([s.lower() for s in service.split(',')]):
                    result.extend(self.getRouteDS(srv, st, tw, geoLoc,
                                                  alternative))
            except ValueError:
                pass

            except RoutingException:
                pass

        if (result is None) or (not len(result)):
            # Through an exception if there is an error
            raise RoutingException('No routes found!')

        return result

    def vn2real(self, stream, tw):
        """Transform from a virtual network code to a list of streams.

        :param stream: requested stream including virtual network code.
        :type stream: Stream
        :param tw: time window requested.
        :type tw: TW
        :returns: Streams and time windows of real network-station codes.
        :rtype: list
        """
        if stream.n not in self.vnTable.keys():
            return [(stream, tw)]

        # If virtual networks are defined with open start or end dates
        # or if there is no intersection, that is resolved in the try

        # Remove the virtual network code to avoid problems in strictMatch
        auxStr = ('*', stream.s, stream.l, stream.c)

        result = list()
        for strtw in self.vnTable[stream.n]:
            try:
                s = strtw[0].strictMatch(auxStr)
            except Exception:
                # Overlap or match cannot be calculated between streams
                continue

            try:
                auxSt, auxEn = strtw[1].intersection(tw)
                t = TW(auxSt if auxSt is not None else None,
                       auxEn if auxEn is not None else None)
            except Exception:
                continue

            result.append((s, t))

        return result

    def getRouteDS(self, service, stream, tw, geoLocation=None,
                   alternative=False):
        """Return routes to request data for the parameters specified.

        Based on a :class:`~Stream` and a timewindow (:class:`~TW`) returns
        all the needed information (URLs and parameters) to request waveforms
        from different datacenters (if needed) and be able to merge it avoiding
        duplication.

        :param service: Specifies the service is being looked for
        :type service: string
        :param stream: :class:`~Stream` definition including wildcards
        :type stream: :class:`~Stream`
        :param tw: Timewindow
        :type tw: :class:`~TW`
        :param geoLocation: Rectangle restricting the location of the station
        :type geoLocation: :class:`~geoRectangle`
        :param alternative: Specifies whether alternative routes should be
            included
        :type alternative: bool
        :returns: URLs and parameters to request the data
        :rtype: :class:`~RequestMerge`
        :raises: RoutingException, ValueError

        """
        # Create list to store results
        subs = list()
        subs2 = list()

        # Filter by stream
        for stRT in self.routingTable.keys():
            if stRT.overlap(stream):
                subs.append(stRT)

        # print('subs', subs)

        # Filter by service and timewindow
        for stRT in subs:
            priorities = list()
            for rou in self.routingTable[stRT]:
                # If it is the proper service and the timewindow coincides
                # with the one in the parameter, add the priority to use it
                # in the last check
                # FIXME The method overlap below does NOT work if I swap
                # rou.tw and tw. For instance, check with:
                # TW(start=None, end=None) TW(start=datetime(1993, 1, 1, 0, 0),
                # end=None)
                if (service == rou.service) and (rou.tw.overlap(tw)):
                    priorities.append(rou.priority)
                else:
                    priorities.append(None)

            if not len([x for x in priorities if x is not None]):
                continue

            if not alternative:
                # Retrieve only the lowest value of priority
                prio2retrieve = [min(x for x in priorities if x is not None)]
            else:
                # Retrieve all alternatives. Don't care about priorities
                prio2retrieve = [x for x in priorities if x is not None]

            # print(prio2retrieve)

            for pos, p in enumerate(priorities):
                if p not in prio2retrieve:
                    continue

                # Add tuples with (Stream, Route)
                subs2.append((stRT, self.routingTable[stRT][pos]))

                # If I don't want the alternative take only the first one
                # if not alternative:
                #     break

        # print('subs2', subs2)

        finalset = list()

        # Reorder to have higher priorities first
        priorities = [rt.priority for (st, rt) in subs2]
        subs3 = [x for (y, x) in sorted(zip(priorities, subs2))]

        # print('subs3', subs3)

        for (s1, r1) in subs3:
            for (s2, r2) in finalset:
                if s1.overlap(s2) and r1.tw.overlap(r2.tw):
                    if not alternative:
                        self.logs.error('%s OVERLAPS\n %s\n' %
                                        ((s1, r1), (s2, r2)))
                        break

                    # Check that the priority is different! Because all
                    # the other attributes are the same or overlap
                    if r1.priority == r2.priority:
                        self.logs.error('Overlap between %s and %s\n' %
                                        ((s1, r1), (s2, r2)))
                        break
            else:
                # finalset.add(r1.strictMatch(stream))
                finalset.append((s1, r1))
                continue

        result = RequestMerge()

        # In finalset I have all the streams (including expanded and
        # the ones with wildcards), that I need to request.
        # Now I need the URLs
        self.logs.debug('Selected streams and routes: %s\n' % finalset)

        while finalset:
            (st, ro) = finalset.pop()

            # Requested timewindow
            setTW = set()
            setTW.add(tw)

            # We don't need to loop as routes are already ordered by
            # priority. Take the first one!
            while setTW:
                toProc = setTW.pop()
                self.logs.debug('Processing %s\n' % str(toProc))

                # Check if the timewindow is encompassed in the returned dates
                self.logs.debug('%s in %s = %s\n' % (str(toProc),
                                                     str(ro.tw),
                                                     (toProc in ro.tw)))
                if (toProc in ro.tw):

                    # If the timewindow is not complete then add the missing
                    # ranges to the tw set.
                    for auxTW in toProc.difference(ro.tw):
                        # Skip the case that we fall always in the same time
                        # span
                        if auxTW == toProc:
                            break
                        self.logs.debug('Adding %s\n' % str(auxTW))
                        setTW.add(auxTW)

                    # Check here that the final result is compatible with the
                    # stations in cache
                    ptST = self.stationTable[urlparse(ro.address).netloc]
                    for cacheSt in ptST[st]:
                        # Trying to catch cases like (APE, AP*)
                        # print st
                        # print cacheSt

                        if (fnmatch.fnmatch(cacheSt.name, stream.s) and
                                ((geoLocation is None) or
                                 (geoLocation.contains(cacheSt.latitude,
                                                       cacheSt.longitude)))):
                            try:
                                auxSt, auxEn = toProc.intersection(ro.tw)
                                twAux = TW(auxSt if auxSt is not None else '',
                                           auxEn if auxEn is not None else '')
                                st2add = stream.strictMatch(st)
                                # In case that routes have to be filter by
                                # location, station names have to be expanded
                                if geoLocation is not None:
                                    st2add = st2add.strictMatch(
                                        Stream('*', cacheSt.name, '*', '*'))

                                # print('Add %s' % str(st2add))

                                result.append(service, ro.address, ro.priority
                                              if ro.priority is not None
                                              else '', st2add, twAux)
                            except Exception:
                                pass

                            # If we don't filter by location, one route covers
                            # everything but if we do filter by location, we
                            # need to keep adding stations
                            if geoLocation is None:
                                break
                    else:
                        msg = "Skipping %s as station %s not in its cache"
                        logging.debug(msg % (str(stream.strictMatch(st)),
                                             stream.s))

        # Check the coherency of the routes to set the return code
        if len(result) == 0:
            raise RoutingException('No routes have been found!')

        return result

    def updateAll(self):
        """Read the two sources of routing information."""
        self.logs.debug('Entering updateAll()\n')
        self.update()

    def updateVN(self):
        """Read the virtual networks defined.

        Stations listed in each virtual network are read into a dictionary.
        Only the necessary attributes are stored. This relies on the idea
        that some other agent should update the routing file at
        a regular period of time.

        """
        self.logs.debug('Entering updateVN()\n')
        # Just to shorten notation
        ptVN = self.vnTable

        try:
            vnHandle = open(self.routingFile, 'r')
        except Exception:
            msg = 'Error: %s could not be opened.\n'
            self.logs.error(msg % self.routingFile)
            return

        # Traverse through the virtual networks
        # get an iterable
        try:
            context = ET.iterparse(vnHandle, events=("start", "end"))
        except IOError as e:
            self.logs.error(str(e))
            return

        # turn it into an iterator
        context = iter(context)

        # get the root element
        if hasattr(context, 'next'):
            event, root = context.next()
        else:
            event, root = next(context)

        # Check that it is really an inventory
        if root.tag[-len('routing'):] != 'routing':
            msg = 'The file parsed seems not to be a routing file (XML).\n'
            self.logs.error(msg)
            return

        # Extract the namespace from the root node
        namesp = root.tag[:-len('routing')]

        ptVN.clear()

        for event, vnet in context:
            # The tag of this node should be "route".
            # Now it is not being checked because
            # we need all the data, but if we need to filter, this
            # is the place.
            #
            if event == "end":
                if vnet.tag == namesp + 'vnetwork':

                    # Extract the network code
                    try:
                        vnCode = vnet.get('networkCode')
                        if len(vnCode) == 0:
                            vnCode = None
                    except Exception:
                        vnCode = None

                    # Traverse through the sources
                    # for arcl in route.findall(namesp + 'dataselect'):
                    for stream in vnet:
                        # Extract the networkCode
                        msg = 'Only the * wildcard is allowed in virtual nets.'
                        try:
                            net = stream.get('networkCode')
                            if (('?' in net) or
                                    (('*' in net) and (len(net) > 1))):
                                self.logs.warning(msg)
                                continue
                        except Exception:
                            net = '*'

                        # Extract the stationCode
                        try:
                            sta = stream.get('stationCode')
                            if (('?' in sta) or
                                    (('*' in sta) and (len(sta) > 1))):
                                self.logs.warning(msg)
                                continue
                        except Exception:
                            sta = '*'

                        # Extract the locationCode
                        try:
                            loc = stream.get('locationCode')
                            if (('?' in loc) or
                                    (('*' in loc) and (len(loc) > 1))):
                                self.logs.warning(msg)
                                continue
                        except Exception:
                            loc = '*'

                        # Extract the streamCode
                        try:
                            cha = stream.get('streamCode')
                            if (('?' in cha) or
                                    (('*' in cha) and (len(cha) > 1))):
                                self.logs.warning(msg)
                                continue
                        except Exception:
                            cha = '*'

                        try:
                            auxStart = stream.get('start')
                            startD = str2date(auxStart)
                        except Exception:
                            startD = None
                            msg = 'Error while converting START attribute.\n'
                            self.logs.error(msg)

                        try:
                            auxEnd = stream.get('end')
                            endD = str2date(auxEnd)
                        except Exception:
                            endD = None
                            msg = 'Error while converting END attribute.\n'
                            self.logs.error(msg)

                        if vnCode not in ptVN:
                            ptVN[vnCode] = [(Stream(net, sta, loc, cha),
                                             TW(startD, endD))]
                        else:
                            ptVN[vnCode].append((Stream(net, sta, loc, cha),
                                                 TW(startD, endD)))

                        stream.clear()

                    vnet.clear()

                # FIXME Probably the indentation below is wrong.
                root.clear()

    def endpoints(self):
        """Read the list of endpoints from the configuration file.

        :returns: List of URLs from endpoints including this RS instance
        :rtype: str

        """
        self.logs.debug('Entering endpoints()\n')

        # Read cfg file
        config = configparser.RawConfigParser()
        self.logs.debug(self.configFile)
        with open(self.configFile, encoding='utf-8') as c:
            config.read_file(c)

        if not config.has_section('Service'):
            return ''

        result = list()

        # Add this RS endpoint
        if 'baseurl' in config.options('Service'):
            result.append(config.get('Service', 'baseurl'))

        if 'synchronize' in config.options('Service'):

            synchroList = config.get('Service', 'synchronize')

            # Loop for the data centres which should be integrated
            for line in synchroList.splitlines():
                if not len(line):
                    break
                dcid, url = line.split(',')
                result.append(url.strip())

        return '\n'.join(result)

    def update(self):
        """Read the routing data from the file saved by the off-line process.

        All the routing information is read into a dictionary. Only the
        necessary attributes are stored. This relies on the idea that some
        other agent should update the routing data at a regular period of time.

        """
        self.logs.debug('Entering update()\n')

        # Otherwise, default value
        synchroList = ''
        allowOverlaps = False

        config = configparser.RawConfigParser()
        try:
            self.logs.debug(self.configFile)
            with open(self.configFile, encoding='utf-8') as c:
                config.readfp(c)

            if 'synchronize' in config.options('Service'):
                synchroList = config.get('Service', 'synchronize')
        except Exception:
            pass

        try:
            if 'allowOverlaps' in config.options('Service'):
                allowOverlaps = config.getboolean('Service', 'allowoverlap')
        except Exception:
            pass

        self.logs.debug(synchroList)
        self.logs.debug('allowOverlaps: %s' % allowOverlaps)

        # Just to shorten notation
        ptRT = self.routingTable
        ptVN = self.vnTable

        # Clear all previous information
        ptRT.clear()
        ptVN.clear()
        binFile = self.routingFile + '.bin'
        try:
            with open(binFile, 'rb') as rMerged:
                self.routingTable, self.stationTable, self.vnTable, self.eidaDCs = \
                    pickle.load(rMerged)
        except Exception:
            ptRT = addRoutes(self.routingFile, allowOverlaps=allowOverlaps)
            ptVN = addVirtualNets(self.routingFile)
            # Loop for the data centres which should be integrated
            for line in synchroList.splitlines():
                if not len(line):
                    break
                self.logs.debug(str(line.split(',')))
                dcid, url = line.split(',')

                if os.path.exists(os.path.join(os.getcwd(), 'data',
                                               'routing-%s.xml' %
                                               dcid.strip())):
                    # addRoutes should return no Exception ever and skip
                    # a problematic file returning a coherent version of the
                    # routes
                    self.logs.debug('Routes in table: %s' % len(ptRT))
                    self.logs.debug('Adding REMOTE %s' % dcid)
                    ptRT = addRoutes(os.path.join(os.getcwd(), 'data',
                                                  'routing-%s.xml' %
                                                  dcid.strip()),
                                     routingTable=ptRT,
                                     allowOverlaps=allowOverlaps)
                    ptVN = addVirtualNets(os.path.join(os.getcwd(), 'data',
                                                       'routing-%s.xml' %
                                                       dcid.strip()),
                                          vnTable=ptVN)

            # Set here self.stationTable
            self.stationTable = dict()
            cacheStations(ptRT, self.stationTable)

            with open(binFile, 'wb') \
                    as finalRoutes:
                self.logs.debug('Writing %s\n' % binFile)
                pickle.dump((ptRT, self.stationTable, ptVN, self.eidaDCs), finalRoutes)
                self.routingTable = ptRT
