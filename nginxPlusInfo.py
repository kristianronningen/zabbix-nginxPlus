#!/usr/bin/python

import requests
import json
from sys import argv
import collections
import argparse

parser = argparse.ArgumentParser(description='This is a simple Python tool that fetches data from nginx+ status api')
parser.add_argument('--url', help='Example: http://localhost:8080/status',default='http://localhost:8080/status')
parser.add_argument('--key', help='Return a specific key using dot notation')
parser.add_argument('--lld-caches', help='Use Zabbix low level discovery to find all caches', action="store_true")
parser.add_argument('--lld-slab-zones', help='Use Zabbix low level discovery to find all SLAB zones', action="store_true")
parser.add_argument('--lld-http-zones', help='Use Zabbix low level discovery to find all HTTP zones', action="store_true")
parser.add_argument('--lld-http-upstreams', help='Use Zabbix low level discovery to find all HTTP upstreams', action="store_true")
parser.add_argument('--lld-stream-zones', help='Use Zabbix low level discovery to find all STREAM zones', action="store_true")
parser.add_argument('--lld-stream-upstreams', help='Use Zabbix low level discovery to find all STREAM upstreams', action="store_true")
parser.add_argument('--debug', help='Dumps all the data in dot notation from the status url', action="store_true")
args = parser.parse_args()

def flatten_json(y, sep='_'):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + sep)
        elif type(x) is list:
            i = 0
            for a in x:
                # If the list has a 'name' value, we want to use that instead
                # of the simple counter. This is true for the 'peers' list
                # inside an upstream definition.
                if a['name']:
                    flatten(a, name + a['name'] + sep)
                else:
                    flatten(a, name + str(i) + sep)
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def main():
  global args
  global parser

  r = requests.get(args.url)
  if r.status_code == 200:

    if args.key:
      d = flatten_json(r.json(),'.')
      print d[args.key]

    if args.lld_caches:
      s = { 'data': [] }
      d = r.json()
      caches = d['caches']
      for k in caches:
        s['data'].append({'{#CACHE_NAME}':k})
      print json.dumps(s)

    if args.lld_slab_zones:
      s = { 'data': [] }
      d = r.json()
      slab_zones = d['slabs']
      for k in slab_zones:
        s['data'].append({'{#SLAB_ZONE}':k})
      print json.dumps(s)

    if args.lld_http_zones:
      s = { 'data': [] }
      d = r.json()
      http_server_zones = d['server_zones']
      for k in http_server_zones:
        s['data'].append({'{#HTTP_SERVER_ZONE}':k})
      print json.dumps(s)

    if args.lld_http_upstreams:
      s = { 'data': [] }
      d = r.json()
      http_upstreams = d['upstreams']
      for k in http_upstreams:
        for p in http_upstreams[k]['peers']:
          s['data'].append({'{#HTTP_UPSTREAM_NAME}':k, '{#HTTP_UPSTREAM_PEER}':p['name']})
      print json.dumps(s)

    if args.lld_stream_zones:
      s = { 'data': [] }
      d = r.json()
      stream_server_zones = d['stream']['server_zones']
      for k in stream_server_zones:
        s['data'].append({'{#STREAM_SERVER_ZONE}':k})
      print json.dumps(s)

    if args.lld_stream_upstreams:
      s = { 'data': [] }
      d = r.json()
      stream_upstreams = d['stream']['upstreams']
      for k in stream_upstreams:
        for p in stream_upstreams[k]['peers']:
          s['data'].append({'{#STREAM_UPSTREAM_NAME}':k, '{#STREAM_UPSTREAM_PEER}':p['name']})
      print json.dumps(s)

    if args.debug:
      print json.dumps(flatten_json(r.json(), '.'), sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
  main()
