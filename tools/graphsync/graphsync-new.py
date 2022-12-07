#!/usr/bin/env python3

# TODO: also support simple list of URLs as dataset file format?

# standard library imports
import sys
import os
import os.path
import email.utils
import datetime
import time
import argparse
import configparser
import logging
import subprocess
import importlib
from contextlib import closing

# external library imports
import pyinotify
import requests
from rdflib import Graph, URIRef, Literal, RDF, RDFS, Namespace, plugin
from rdflib.store import Store


VOID = Namespace('http://rdfs.org/ns/void#')
SKOSMOS = Namespace('http://purl.org/net/skosmos#')
DCT = Namespace('http://purl.org/dc/terms/')

class GraphSyncer:
  datasetfile = None
  metagraph = None
  posthookcmd = None
  singleshot = False
  
  def __init__(self, datasetfile, query_endpoint, update_endpoint, metadata_graph, posthookcmd, wait_after_update, singleshot):
    self.logger = logging.getLogger(__name__)
    self.datasetfile = datasetfile
    self.update_endpoint = update_endpoint
    sparqlstore = plugin.get('SPARQLUpdateStore',Store)(query_endpoint, update_endpoint)
    self.metagraph = Graph(sparqlstore, URIRef(metadata_graph))
    self.posthookcmd = posthookcmd
    self.wait_after_update = wait_after_update
    self.singleshot = singleshot
    
  def load_sources(self):
    self.logger.debug("parsing dataset file %s", self.datasetfile)
    sources = {}
    vocgraph = Graph()
    try:
      vocgraph.parse(self.datasetfile, format='turtle')
    except Exception as e:
      self.logger.critical("parsing dataset file %s failed: %s", self.datasetfile, e)
      return sources
    for ds,srcurl in vocgraph.subject_objects(VOID.dataDump):
      graphuri = vocgraph.value(ds, SKOSMOS.sparqlGraph, None)
      if srcurl.endswith('.ttl'): # quick fix for problems with multiple dumps
        sources[srcurl] = graphuri
    self.logger.debug("found %d sources", len(sources))
    return sources

  def get_newer(self, srcurl, graphuri):
    # find out timestamp of source URL by doing a streaming GET request (only get the headers)
    with closing(requests.get(srcurl, stream=True, headers={'Pragma': 'no-cache'})) as response:
      try:
        response.raise_for_status()
        lastmodhdr = response.headers['Last-Modified']
      except requests.exceptions.RequestException as e:
        self.logger.warning("Failed to request modification time from source <%s>: %s", srcurl, e)
        return None

    # parse and make the Last-Modified timestamp into an ISO 8601 date string
    ts = email.utils.mktime_tz(email.utils.parsedate_tz(lastmodhdr))
    srcmod = datetime.datetime.utcfromtimestamp(ts).isoformat() + 'Z'
    
    # find out what the current timestamp and source URL is in the SPARQL store
    try:
      graphmod = str(self.metagraph.value(graphuri, DCT.modified, None))
      graphsrc = self.metagraph.value(graphuri, DCT.source, None)
    except Exception as e:
      self.logger.warning("Failed to request metadata for graph <%s>: %s", graphuri, e)
      return None

    self.logger.debug("comparing timestamps, source: %s, graph: %s, equal: %s", srcmod, graphmod, srcmod==graphmod)
    self.logger.debug("comparing URLs, source: <%s>, graph: <%s>, equal: %s", srcurl, graphsrc, srcurl==graphsrc)
    if graphmod is not None and graphsrc is not None and srcmod == graphmod and srcurl == graphsrc:
      self.logger.debug("no need to refresh")
      return None
    self.logger.debug("need to refresh")
    return srcmod
  
  def update_graph(self, srcurl, graphuri, new_ts):
    self.logger.info("updating graph <%s> from <%s>, timestamp: %s", graphuri, srcurl, new_ts)
    # issue SPARQL LOAD command
    loadcmd = "CLEAR GRAPH <%s>; LOAD <%s> INTO GRAPH <%s>" % (graphuri, srcurl, graphuri)
    try:
      response = requests.post(self.update_endpoint, data=loadcmd, headers={'Content-Type': 'application/sparql-update'})
      response.raise_for_status()
    except requests.exceptions.RequestException as e:
      self.logger.warning("SPARQL Update LOAD command failed for graph <%s> from <%s>: %s", graphuri, srcurl, e)
      return
    
    try:
      # update timestamp and source URL in metadata graph
      # note: this may be slightly old if the data has just changed, but a subsequent run will fix it anyway
      self.metagraph.remove((graphuri, DCT.modified, None))
      self.metagraph.remove((graphuri, DCT.source, None))
      self.metagraph.add((graphuri, DCT.modified, Literal(new_ts)))
      self.metagraph.add((graphuri, DCT.source, URIRef(srcurl)))
    except Exception as e:
      self.logger.warning("Failed to update metadata for graph <%s>: %s", graphuri, e)
    
    self.logger.info("waiting %d seconds after update" % self.wait_after_update)
    time.sleep(self.wait_after_update)
  
  def post_hook(self):
    self.logger.info("calling post-update hook %s", self.posthookcmd)
    try:
      p = subprocess.Popen([self.posthookcmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = p.communicate()
      self.logger.debug("post-update hook output: %s", stdout)
      if stderr:
        self.logger.warning("post-update hook error output: %s", stderr)
    except Exception as e:
      self.logger.warning("Failed to run post-update hook %s: %s", self.posthookcmd, e)
    
  def sync(self):
    self.logger.info("performing synchronization")

    cleanrun = False
    updated = False
    while not cleanrun:
      # load new data until there is nothing more to load, i.e. fully up to date
      refresh = False
      sources = self.load_sources()
      
      for srcurl, graphuri in sorted(sources.items()):
        self.logger.debug("checking graph <%s> from <%s>", graphuri, srcurl)
        new_ts = self.get_newer(srcurl, graphuri)
        if new_ts is not None:
          self.update_graph(srcurl, graphuri, new_ts)
          refresh = True
          updated = True
      
      if not refresh:
        self.logger.debug("clean run performed, no more updates")
        cleanrun = True
    
    if updated:
      self.logger.debug("calling post-update hook")
      self.post_hook()
      self.logger.info("synchronization done, updates performed")
    else:
      self.logger.info("synchronization done, no updates performed")
    if self.singleshot:
      self.logger.debug("single-shot mode, exiting")
      sys.exit()


class Handler (pyinotify.ProcessEvent):
  def __init__(self, syncer):
    self.syncer = syncer
    self.logger = logging.getLogger(__name__)

  def process_IN_CLOSE_WRITE(self, event=None):
    # this will be called whenever the dataset file changes
    self.logger.info("dataset file change detected")
    self.syncer.sync()

  def on_loop(self, n):
    # this will be called at startup, and with intervals specified by timeout
    self.logger.info("starting periodic check")
    self.syncer.sync()

class App:
  def __init__(self, args, cfg, wdir):
    self.args = args
    self.cfg = cfg
    self.wdir = wdir

  def run(self, singleshot=False):
    datasetfile = self.cfg.get('graphsync', 'dataset_file')
    posthookcmd = self.cfg.get('graphsync', 'post_hook')
    logfile = self.cfg.get('graphsync', 'log_file')
    query_endpoint = self.cfg.get('graphsync', 'query_endpoint')
    update_endpoint = self.cfg.get('graphsync', 'update_endpoint')
    metadata_graph = self.cfg.get('graphsync', 'metadata_graph')
    check_interval = self.cfg.getint('graphsync', 'check_interval')
    wait_after_update = self.cfg.getint('graphsync', 'wait_after_update')

    # initialize logging
    if self.args.debug:
      loglevel = logging.DEBUG
    else:
      loglevel = logging.INFO

    logger = logging.getLogger(__name__)
    if self.args.debug:
      logger.setLevel(logging.DEBUG)
    else:
      logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # set up basic logging on stderr (will go to /dev/null in daemon mode)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # additionally output to log file if set
    if logfile:
      fh = logging.FileHandler(os.path.join(self.wdir, logfile))
      fh.setFormatter(formatter)
      logger.addHandler(fh)
    
    logger.info("graphsync $Rev: 1294 $ starting up")
    logger.debug("watching dataset file %s", datasetfile)
    logger.debug("check_interval set to %s seconds", check_interval)
    logger.debug("wait_after_update set to %s seconds", wait_after_update)

    # initialize the syncer
    datasetfile = os.path.join(self.wdir, datasetfile)
    syncer = GraphSyncer(datasetfile, query_endpoint, update_endpoint, metadata_graph, posthookcmd, wait_after_update, singleshot)

    wm = pyinotify.WatchManager()
    handler = Handler(syncer)
    notifier = pyinotify.Notifier(wm, handler, timeout=check_interval * 1000) # seconds to ms
    wm.add_watch(datasetfile, pyinotify.IN_CLOSE_WRITE)
    notifier.loop(callback=handler.on_loop)


# parse command line
parser = argparse.ArgumentParser(description='Synchronize RDF graphs from source URLs to a SPARQL endpoint.')
group = parser.add_mutually_exclusive_group()
group.add_argument('-D', '--debug', action='store_true', help='enable debug output')
group.add_argument('-s', '--single', action='store_true', help='single shot mode (run once, then exit)')
parser.add_argument('config', type=argparse.FileType('r'), help='configuration file')
args = parser.parse_args()

# read configuration file
cfg = configparser.ConfigParser()
cfg.readfp(args.config)

# initialize App instance
app = App(args, cfg, os.getcwd())

app.run(singleshot=args.single)
