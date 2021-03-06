"""
Pulp Interactive Client
This module is meant to be imported to talk to pulp webservices interactively
from an interpreter. It provides convenience methods for connecting to pulp as
well as performing many common pulp tasks.
"""

import base64
import httplib
import json
import os
import ssl
import sys
import types
import urllib


HOST = 'localhost'
PORT = 443
PATH_PREFIX = '/pulp/api'
AUTH_SCHEME = 'basic'  # can also be 'oauth' (XXX not really)
USER = 'admin'
PASSWORD = 'admin'

LOG_BODIES = True


_CONNECTION = None


def connect(verify_ssl=True):
    global _CONNECTION
    if verify_ssl:
        _CONNECTION = httplib.HTTPSConnection(HOST, PORT)
    else:
        insecure_context = ssl._create_unverified_context()
        _CONNECTION = httplib.HTTPSConnection(HOST, PORT, context=insecure_context)


def set_basic_auth_credentials(user, password):
    global AUTH_SCHEME, USER, PASSWORD
    AUTH_SCHEME = 'basic'
    USER = user
    PASSWORD = password


class RequestError(Exception):
    pass


def _auth_header():
    def _basic_auth_header():
        raw = ':'.join((USER, PASSWORD))
        encoded = base64.encodestring(raw)[:-1]
        return {'Authorization': 'Basic %s' % encoded}

    def _oauth_header():
        return {}

    if AUTH_SCHEME == 'basic':
        return _basic_auth_header()
    if AUTH_SCHEME == 'oauth':
        return _oauth_header()
    return {}


def _request(method, path, body=None):
    if _CONNECTION is None:
        raise RuntimeError('You must run connect() before making requests')

    # Strip off the leading prefix if it's specified to aid in copy/paste usage
    if path.startswith(PATH_PREFIX):
        path = path[len(PATH_PREFIX):]

    if not isinstance(body, types.NoneType):
        body = json.dumps(body, indent=2)

        if LOG_BODIES:
            print('Request Body')
            print(body)

    _CONNECTION.request(method,
                        PATH_PREFIX + path,
                        body=body,
                        headers=_auth_header())
    response = _CONNECTION.getresponse()
    response_body = response.read()
    try:
        response_body = json.loads(response_body)

        if LOG_BODIES:
            print('Response Body')
            print(json.dumps(response_body, indent=2))

    except:
        pass
    if response.status > 299:
        raise RequestError('Server response: %d\n%s' %
                           (response.status, response_body))
    return (response.status, response_body)


def GET(path, **params):
    if params:
        path = '?'.join((path, urllib.urlencode(params)))
    return _request('GET', path)


def OPTIONS(path):
    return _request('OPTIONS', path)


def PUT(path, body):
    return _request('PUT', path, body)


def POST(path, body=None):
    return _request('POST', path, body)


def DELETE(path):
    return _request('DELETE', path)


def list_repos():
    return GET('/repositories/')


def get_repo(id):
    return GET('/repositories/%s/' % id)


def create_repo(id, name=None, arch='noarch', **kwargs):
    """
    Acceptable keyword arguments are any arguments for a new Repo model.
    Common ones are: feed and sync_schedule
    """
    kwargs.update({'id': id, 'name': name or id, 'arch': arch})
    return POST('/repositories/', kwargs)


def update_repo(id, **kwargs):
    """
    Acceptable keyword arguments are any arguments for a new Repo model.
    Common ones are: feed and sync_schedule
    """
    return PUT('/repositories/%s/' % id, kwargs)


def delete_repo(id):
    return DELETE('/repositories/%s/' % id)


def schedules():
    """
    List the sync schedules for all the repositories.
    """
    return GET('/repositories/schedules/')


def sync_history(id):
    return GET('/repositories/%s/history/sync/' % id)


def regenerate_content_applicability_for_consumers(consumer_criteria):
    """
    Regenerate content applicability data for given consumers
    """
    options = {"consumer_criteria": consumer_criteria}
    return POST('/pulp/api/v2/consumers/actions/content/regenerate_applicability/', options)


def regenerate_content_applicability_for_repos(repo_criteria):
    """
    Regenerate content applicability data for all consumers affected by given repositories
    """
    options = {"repo_criteria": repo_criteria}
    return POST('/pulp/api/v2/repositories/actions/content/regenerate_applicability/', options)


def register_consumer(consumer_id):
    options = {"id": consumer_id}
    return POST('/pulp/api/v2/consumers/', options)


def query_applicability(consumer_criteria, content_types):
    options = {'criteria': consumer_criteria,
               'content_types': content_types}
    return POST('/pulp/api/v2/consumers/content/applicability/', options)


def create_consumer_profile(consumer_id, content_type, profile):
    options = {'content_type': content_type,
               'profile': profile}
    return POST('/pulp/api/v2/consumers/%s/profiles/' % consumer_id, options)


def replace_consumer_profile(consumer_id, content_type, profile):
    options = {'profile': profile}
    return PUT('/pulp/api/v2/consumers/%s/profiles/%s/' % (consumer_id, content_type),
               options)


def get_consumer_profiles(consumer_id):
    return GET('/v2/consumers/%s/profiles/' % consumer_id)


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    print >> sys.stderr, 'Not a script, import as a module in an interpreter'
    sys.exit(os.EX_USAGE)
