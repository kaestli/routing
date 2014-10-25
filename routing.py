#!/usr/bin/env python
#
# Routing WS prototype
#
# (c) 2014 Javier Quinteros, GEOFON team
# <javier@gfz-potsdam.de>
#
# ----------------------------------------------------------------------

"""
.. module:: routing
   :platform: Linux
   :synopsis: Routing Webservice for EIDA

.. moduleauthor:: Javier Quinteros <javier@gfz-potsdam.de>, GEOFON, GFZ Potsdam
"""

##################################################################
#
# First all the imports
#
##################################################################


import os
import cgi
import datetime
import xml.etree.cElementTree as ET
import ConfigParser
import json
from wsgicomm import WIContentError
from wsgicomm import WIClientError
from wsgicomm import WIError
from wsgicomm import send_plain_response
from wsgicomm import send_xml_response
from utils import RequestMerge
from utils import RoutingCache
from utils import RoutingException


def _ConvertDictToXmlRecurse(parent, dictitem):
    assert not isinstance(dictitem, list)

    if isinstance(dictitem, dict):
        for (tag, child) in dictitem.iteritems():
            if str(tag) == '_text':
                parent.text = str(child)
            elif isinstance(child, list):
                # iterate through the array and convert
                for listchild in child:
                    elem = ET.Element(tag)
                    parent.append(elem)
                    _ConvertDictToXmlRecurse(elem, listchild)
            else:
                elem = ET.Element(tag)
                parent.append(elem)
                _ConvertDictToXmlRecurse(elem, child)
    else:
        parent.text = str(dictitem)


def ConvertDictToXml(listdict):
    """
    Converts a list with dictionaries to an XML ElementTree Element
    """

    r = ET.Element('service')
    for di in listdict:
        d = {'datacenter': di}
        roottag = d.keys()[0]
        root = ET.SubElement(r, roottag)
        _ConvertDictToXmlRecurse(root, d[roottag])
    return r


def makeQueryGET(parameters):
    global routes

    # List all the accepted parameters
    allowedParams = ['net', 'network',
                     'sta', 'station',
                     'loc', 'location',
                     'cha', 'channel',
                     'start', 'starttime',
                     'end', 'endtime',
                     'service', 'format',
                     'alternative']

    for param in parameters:
        if param not in allowedParams:
            return 'Unknown parameter: %s' % param

    try:
        if 'network' in parameters:
            net = parameters['network'].value.upper()
        elif 'net' in parameters:
            net = parameters['net'].value.upper()
        else:
            net = '*'
    except:
        net = '*'

    try:
        if 'station' in parameters:
            sta = parameters['station'].value.upper()
        elif 'sta' in parameters:
            sta = parameters['sta'].value.upper()
        else:
            sta = '*'
    except:
        sta = '*'

    try:
        if 'location' in parameters:
            loc = parameters['location'].value.upper()
        elif 'loc' in parameters:
            loc = parameters['loc'].value.upper()
        else:
            loc = '*'
    except:
        loc = '*'

    try:
        if 'channel' in parameters:
            cha = parameters['channel'].value.upper()
        elif 'cha' in parameters:
            cha = parameters['cha'].value.upper()
        else:
            cha = '*'
    except:
        cha = '*'

    try:
        if 'starttime' in parameters:
            start = datetime.datetime.strptime(
                parameters['starttime'].value[:19].upper(),
                '%Y-%m-%dT%H:%M:%S')
        elif 'start' in parameters:
            start = datetime.datetime.strptime(
                parameters['start'].value[:19].upper(),
                '%Y-%m-%dT%H:%M:%S')
        else:
            start = None
    except:
        raise WIError('400 Bad Request',
                      'Error while converting starttime parameter.')

    try:
        if 'endtime' in parameters:
            endt = datetime.datetime.strptime(
                parameters['endtime'].value[:19].upper(),
                '%Y-%m-%dT%H:%M:%S')
        elif 'end' in parameters:
            endt = datetime.datetime.strptime(
                parameters['end'].value[:19].upper(),
                '%Y-%m-%dT%H:%M:%S')
        else:
            endt = None
    except:
        raise WIError('400 Bad Request',
                      'Error while converting endtime parameter.')

    try:
        if 'service' in parameters:
            ser = parameters['service'].value.lower()
        else:
            ser = 'dataselect'
    except:
        ser = 'dataselect'

    try:
        if 'alternative' in parameters:
            alt = True if parameters['alternative'].value.lower() == 'true'\
                else False
        else:
            alt = False
    except:
        alt = False

    route = routes.getRoute(net, sta, loc, cha, start, endt, ser, alt)

    if len(route) == 0:
        raise WIContentError('No routes have been found!')
    return route


def makeQueryPOST(postText):
    global routes

    # This are the parameters accepted appart from N.S.L.C
    extraParams = ['format', 'service', 'alternative']

    # Defualt values
    ser = 'dataselect'
    alt = False

    result = RequestMerge()
    # Check if we are still processing the header of the POST body. This has a
    # format like key=value, one per line.
    inHeader = True

    for line in postText.splitlines():
        if not len(line):
            continue

        if (inHeader and ('=' not in line)):
            inHeader = False

        if inHeader:
            try:
                key, value = line.split('=')
                key = key.strip()
                value = value.strip()
            except:
                raise WIError('400 Bad Request',
                              'Wrong format detected while processing: %s' %
                              line)

            if key not in extraParams:
                raise WIError('400 Bad Request',
                              'Unknown parameter "%s"' % key)

            if key == 'service':
                ser = value
            elif key == 'alternative':
                alt = True if value.lower() == 'true' else False

            continue

        # I'm already in the main part of the POST body, where the streams are
        # specified
        net, sta, loc, cha, start, endt = line.split()
        net = net.upper()
        sta = sta.upper()
        loc = loc.upper()
        try:
            start = None if start in ("''", '""') else \
                datetime.datetime.strptime(start[:19].upper(),
                                           '%Y-%m-%dT%H:%M:%S')
        except:
            raise WIError('400 Bad Request',
                          'Error while converting %s to datetime' % start)

        try:
            endt = None if endt in ("''", '""') else \
                datetime.datetime.strptime(endt[:19].upper(),
                                           '%Y-%m-%dT%H:%M:%S')
        except:
            raise WIError('400 Bad Request',
                          'Error while converting %s to datetime' % endt)

        try:
            result.extend(routes.getRoute(net, sta, loc, cha,
                                          start, endt, ser, alt))
        except RoutingException:
            pass

    if len(result) == 0:
        raise WIContentError('No routes have been found!')
    return result


def applyFormat(resultRM, outFormat='xml'):
    """Apply the format specified to the RequestMerge object received.
    Returns a STRING with the result
    """

    if not isinstance(resultRM, RequestMerge):
        raise Exception('applyFormat expects a RequestMerge object!')

    if outFormat == 'json':
        iterObj = json.dumps(resultRM, default=datetime.datetime.isoformat)
        return iterObj
    elif outFormat == 'get':
        iterObj = []
        for datacenter in resultRM:
            for item in datacenter['params']:
                iterObj.append(datacenter['url'] + '?' +
                               '&'.join([k + '=' + str(item[k]) for k in item
                                         if item[k] not in ('', '*')
                                         and k != 'priority']))
        iterObj = '\n'.join(iterObj)
        return iterObj
    elif outFormat == 'post':
        iterObj = []
        for datacenter in resultRM:
            iterObj.append(datacenter['url'])
            for item in datacenter['params']:
                item['loc'] = item['loc'] if len(item['loc']) else '--'
                iterObj.append(item['net'] + ' ' + item['sta'] + ' ' +
                               item['loc'] + ' ' + item['cha'] + ' ' +
                               item['start'] + ' ' + item['end'])
            iterObj.append('')
        iterObj = '\n'.join(iterObj)
        return iterObj
    else:
        iterObj2 = ET.tostring(ConvertDictToXml(resultRM))
        return iterObj2

# This variable will be treated as GLOBAL by all the other functions
routes = None


def application(environ, start_response):
    """Main WSGI handler that processes client requests and calls
    the proper functions.

    Begun by Javier Quinteros <javier@gfz-potsdam.de>,
    GEOFON team, February 2014

    """

    global routes
    fname = environ['PATH_INFO']

    # Among others, this will filter wrong function names,
    # but also the favicon.ico request, for instance.
    if fname is None:
        raise WIClientError('Method name not recognized!')
        # return send_html_response(status, 'Error! ' + status, start_response)

    try:
        outForm = 'xml'

        if environ['REQUEST_METHOD'] == 'GET':
            form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
            if 'format' in form:
                outForm = form['format'].value.lower()
        elif environ['REQUEST_METHOD'] == 'POST':
            form = ''
            try:
                length = int(environ.get('CONTENT_LENGTH', '0'))
            except ValueError:
                length = 0

            # If there is a body to read
            if length != 0:
                form = environ['wsgi.input'].read(length)
            else:
                form = environ['wsgi.input'].read()

            for line in form.splitlines():
                if not len(line):
                    continue

                if '=' not in line:
                    break
                k, v = line.split('=')
                if k.strip() == 'format':
                    outForm = v.strip()

        else:
            raise Exception

    except ValueError, e:
        if str(e) == "Maximum content length exceeded":
            # Add some user-friendliness (this message triggers an alert
            # box on the client)
            return send_plain_response("400 Bad Request",
                                       "maximum request size exceeded",
                                       start_response)

        return send_plain_response("400 Bad Request", str(e), start_response)

    # Check whether the function called is implemented
    implementedFunctions = ['query', 'application.wadl', 'localconfig',
                            'version', 'info']

    if routes is None:
        # Add routing cache here, to be accessible to all modules
        here = os.path.dirname(__file__)
        routesFile = os.path.join(here, 'routing.xml')
        invFile = os.path.join(here, 'Arclink-inventory.xml')
        masterFile = os.path.join(here, 'masterTable.xml')
        routes = RoutingCache(routesFile, invFile, masterFile)

    fname = environ['PATH_INFO'].split('/')[-1]
    if fname not in implementedFunctions:
        return send_plain_response("400 Bad Request",
                                   'Function "%s" not implemented.' % fname,
                                   start_response)

    if fname == 'application.wadl':
        iterObj = ''
        here = os.path.dirname(__file__)
        appWadl = os.path.join(here, 'application.wadl')
        with open(appWadl, 'r') \
                as appFile:
            iterObj = appFile.read()
            status = '200 OK'
            return send_xml_response(status, iterObj, start_response)

    elif fname == 'query':
        makeQuery = globals()['makeQuery%s' % environ['REQUEST_METHOD']]
        try:
            iterObj = makeQuery(form)

            iterObj = applyFormat(iterObj, outForm)

            status = '200 OK'
            if outForm == 'xml':
                return send_xml_response(status, iterObj, start_response)
            else:
                return send_plain_response(status, iterObj, start_response)

        except WIError as w:
            return send_plain_response(w.status, w.body, start_response)

    elif fname == 'localconfig':
        return send_xml_response('200 OK', routes.localConfig(),
                                 start_response)

    elif fname == 'version':
        text = "1.0.0"
        return send_plain_response('200 OK', text, start_response)

    elif fname == 'info':
        config = ConfigParser.RawConfigParser()
        here = os.path.dirname(__file__)
        config.read(os.path.join(here, 'routing.cfg'))

        text = config.get('Service', 'info')
        return send_plain_response('200 OK', text, start_response)

    raise Exception('This point should have never been reached!')


def main():
    routes = RoutingCache("./routing.xml", "./Arclink-inventory.xml",
                          "./masterTable.xml")
    print len(routes.routingTable)


if __name__ == "__main__":
    main()
