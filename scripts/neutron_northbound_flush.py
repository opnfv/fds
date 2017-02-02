#! /usr/bin/env python
import yaml
import json
import urlparse
import urllib3
import logging
import argparse

http = urllib3.PoolManager()
logger_name='neutron_nb_flush'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/tmp/{}.log'.format(logger_name))
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(file_handler)


def _request(method, url, credentials):
    headers = urllib3.make_headers(basic_auth=credentials)
    return http.request(method, url, headers=headers)


def _del(url, credentials=None):
    logger.info('Deleting url {}'.format(url))
    return _request('DELETE', url, credentials=credentials)


def _get(url, credentials=None):
    return _request('GET', url, credentials=credentials)


def _get_ids(url, credentials, key):
    ids = []
    try:
        res_data = json.loads(_get('{}'.format(url), credentials=credentials).data)
        entries_keys = res_data.keys()
        entries = res_data[entries_keys[0]]

        for entry in entries:
            ids.append(entry[key])

    except ValueError as e:
        logger.warning("Get on url {} didn't return a json. Skipping, full error: {}".format(url, e))

    finally:
        return ids


def delete_all(url, credentials, key):
    ids = _get_ids(url, credentials, key)
    if len(ids) > 0:
        logger.info("Found entries with ids {} in {}, attempting to delete them".format(', '.join(ids), url))
        if ids is not None:
            for resource_id in ids:
                del_url = '/'.join([url, resource_id])
                _del(del_url, credentials)
    else:
        logger.info("No entries found in {}".format(url))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Remove all data in odls' neutron northbound")
    parser.add_argument('-c', '--config-yaml', default='data/neutron_nb_uris.yaml',
                        help='The input config yaml')

    args = parser.parse_args()
    with open(args.config_yaml) as yaml_buf:
        yaml_conf = yaml.load(yaml_buf)

    scheme = yaml_conf['scheme']
    host = yaml_conf['host']
    port = yaml_conf['port']
    username = yaml_conf['username']
    password = yaml_conf['password']
    list_key = yaml_conf['key']

    mysql_credentials = ':'.join((username, password))
    netloc = ':'.join((host, str(port)))
    base = '://'.join((scheme, netloc))

    neutron_nb_urls = []
    for uri in yaml_conf['odl_nb_uris']:
        odl_nb_url = urlparse.urljoin(base, uri)
        logger.info('Parsed url {}'.format(odl_nb_url))
        neutron_nb_urls.append(odl_nb_url)

    for neutron_nb_url in neutron_nb_urls:
        delete_all(neutron_nb_url, mysql_credentials, list_key)
