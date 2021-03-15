#!/usr/bin/env python
import argparse, os, requests, json
from netaddr import *
from pygrok import Grok
from elasticsearch import Elasticsearch
from threading import Thread, BoundedSemaphore

class multi_push(Thread):
    def __init__(self, lines_in_log, lines_in_ipmatch, subnet):
      Thread.__init__(self)
      self.lines_in_log = lines_in_log
      self.lines_in_ipmatch = lines_in_ipmatch
      self.subnet = subnet
    def run(self):
        threadLimiter.acquire()
        net = IPNetwork(subnet)
        pattern = '%{DATA:username}  %{IPORHOST:clientip} %{USER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] "%{WORD:verb} %{URIPATHPARAM:request} HTTP/%{NUMBER:httpversion}" %{NUMBER:response} (?:%{NUMBER:bytes}|-) (?:"(?:%{URI:referrer}|-)"|%{QS:referrer}) %{QS:agent}'
        grok = Grok(pattern)
        es = Elasticsearch([{'host': '192.168.27.67', 'port': '9200'}])
        try:
          for line in lines_in_log:
            src_ip = line.split()[0]
            for ip_match_line in lines_in_ipmatch:
              current_line_list = ip_match_line.split(" | ")
              try:
                if src_ip == current_line_list[1] or src_ip == current_line_list[3]:
                  line = current_line_list[0] + line
              except: line = " " + line

            if src_ip in net:
              try:
                json_line = grok.match(line)
                if args.verbose: print (json.dumps(json_line))
                es.index(index='crm_logs_new_index',  body=json.dumps(json_line))
              except: pass 
        finally:
          threadLimiter.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--net', '-n', default='192.168.27.0/24')
    parser.add_argument('--ipmatch', '-i', default='ip_match.txt')
    parser.add_argument('--verbose', '-v',help='increase output verbosity', action='store_true')
    args = parser.parse_args()
    threadLimiter = BoundedSemaphore(150)
    with open(args.ipmatch, "r") as ipmatch:
      lines_in_ipmatch = ipmatch.readlines()
    subnet = args.net
    for each_log_file in os.listdir('logs'):
      with open('logs/'+each_log_file, "r") as log:
        lines_in_log = log.readlines()
      thread = multi_push(lines_in_log, lines_in_ipmatch, subnet)
      thread.start()
