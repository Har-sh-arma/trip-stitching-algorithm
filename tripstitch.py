# -*- coding: utf-8 -*-
"""tripStitch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZtxNDwuuX72PBIlh7wKc996cLmZrrsnu
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import math
import pprint
import random

pos= []
src = 7
dst = 6
def SimulateData(n):
	global pos
	db = nx.complete_graph(n, nx.DiGraph())
	pos = nx.random_layout(db, seed=0)
	for e in list(db.edges):
		db.edges[e]['dist'] = math.dist(pos[e[0]], pos[e[1]])*10
		db.edges[e]['dura'] = 5*(math.dist(pos[e[0]], pos[e[1]])*10)
	return db

class Route():
	def __init__(self, src, dst, dist):
		self.src = src
		self.dst = dst
		self.dist = dist
	def __str__(self):
		return f"{self.src}----{self.dist}----->{self.dst}"

# this is to be implemented by service providers
def GetRoutes(missing_links):
	global src
	global dst
	routes = []
	for link in missing_links:
		if(random.randint(0,1) or random.randint(0,1) or (link[0]==src and link[1]==dst)):
			src1 = link[0]
			dst1 = link[1]
			dist = abs(db[src][dst]['dist']-0.5)
			tmp = Route(src1,dst1,dist)
			routes.append(tmp)
	# add few other responses as well
	# select random edges add them to the list
	k = 5
	nodes = list(np.random.choice(range(n), k*2, replace=False))
	for i in range(k):
		src1 = nodes[i]
		dst1 = nodes[i+2]
		dist = abs(db[src1][dst1]['dist']-0.5)
		tmp = Route(src1,dst1,dist)
		routes.append(tmp)

	return routes

def showGraph():
    global transfer_threshold
    # edgeCol1 = []
    # alpha = []
    global pos
    figure, axes = plt.subplots()
    for node in G.nodes:
      c = plt.Circle((pos[node][0], pos[node][1]), transfer_threshold/10, alpha=0.1 )
      axes.add_artist(c)
    nx.draw_networkx_nodes(G, pos )
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(db, pos, edge_color=["blue"]*(n*(n-1)), alpha = [0]*(n*(n-1)))
    nx.draw_networkx_edges(G, pos, edge_color=["black"]*(n*(n-1)))
    nx.draw_networkx_edges(G_n_miss, pos, edge_color=["red"]*(n*(n-1)),  alpha = [0]*(n*(n-1)))
    plt.show()

'''Update the CLient Side Graph to accomodate New Nodes and Edges and decide which missing links to request on next iteration'''

def UpdateGraph(routes):
  for route in routes:
    src1 = route.src
    dst1 = route.dst
    G.add_edge(src1, dst1)
    dist = route.dist
    G[src1][dst1]['dist'] = dist


'''Rank the damn missing links preferable without completing the entire graph'''
# def FilterRankSelectMissingLinks(by='dist'):
# 	# implement a filter, rank, select criteria

# 	n = len(G)
# 	k = 2
# 	nodes = list(np.random.choice(range(n), k*2, replace=False))
# 	missing_links = []
# 	for i in range(k):
# 		src = nodes[i]
# 		dst = nodes[i+2]
# 		missing_links.append([src,dst])
# 	# add filtering creiteria
# 	# TBD
# 	return missing_links

'''Rank Paths'''

#function to create
def evaluate_paths_n_routes(num):
  global src
  global dst
  global paths_dict
  global missing_link_dict
  num = 0
  paths_dict = {} #for ranking paths
  missing_link_dict = {} #for ranking missing links

  '''Adding the shortest paths to evaluate their various parameters

  missing_link length > threshold
  number of transfers
  path length

  '''
  for i in nx.shortest_simple_paths(G_n_miss, src, dst, weight="dist"):
    if(num>20):
      break
    paths_dict[str(i)] = {"num_missing":0,"total_missing_dist":0 , "path_length":0, "num_transfers":0, "transfer_threshold":True}
    num+=1
  '''Adding metrics number of missing links, total '''
  for path_str in paths_dict:
    path = list(map(int, path_str.replace(" ", "")[1:-1].split(",")))
    i = 0
    transfer_flag=False
    while(i<len(path)-1):
      paths_dict[path_str]["path_length"] += db[path[i]][path[i+1]]['dist']
      if(not G.has_edge(path[i],path[i+1])):

          '''path ranking params'''
          paths_dict[path_str]["transfer_threshold"] = paths_dict[path_str]["transfer_threshold"] and (int(db[path[i]][path[i+1]]['dist'])<transfer_threshold)
          paths_dict[path_str]["num_missing"] +=1
          paths_dict[path_str]["total_missing_dist"] += db[path[i]][path[i+1]]['dist'] #here the db dist can be replace by a real world heuristic like geographic distance
          if(not transfer_flag):                                                             #counting transfers consequent transfers count as 1
              paths_dict[path_str]["num_transfers"] +=1
              transfer_flag = True

          '''missing link ranking params'''
          if (path[i],path[i+1]) in missing_link_dict:
              missing_link_dict[(path[i],path[i+1])]["occ_freq"] += 1
          else:
              missing_link_dict[(path[i],path[i+1])] = {"occ_freq":0, "transferable":(db[path[i]][path[i+1]]['dist']<transfer_threshold)}
      else:
        transfer_flag = False

      i+=1

def Update_G_n_miss(G_n_miss):
	for e in list(G_n_miss.edges):
		G_n_miss.edges[e]['dist'] = math.dist(pos[e[0]], pos[e[1]])*10
		if e in list(G.edges):
			G_n_miss.edges[e]['dura'] = 2*(math.dist(pos[e[0]], pos[e[1]])*10)
		else:
			G_n_miss.edges[e]['dura'] = 5*(math.dist(pos[e[0]], pos[e[1]])*10)

	return G_n_miss

def missing_link_update():
	global r
	global src
	global dst
	for i in r:
		if (i.src, i.dst) in missing_links:
			missing_links.remove((i.src, i.dst))

def FilterRankSelectMissingLinks(by=''):
    global missing_link_dict
    for key, value in sorted(missing_link_dict.items(), key=lambda x: x[1]["occ_freq"]):
      if(not value["transferable"]):
        missing_links.append(key)
    return missing_links
    # implement a filter, rank, select criteria

n = 20

db = SimulateData(n)
# current state of the graph
G = nx.DiGraph()

max_dist = 100
stop = False
counter = 0

missing_links = [[src,dst]]
paths_dict = {} #for ranking paths
missing_link_dict = {} #for ranking missing links
transfer_threshold = 1

while(counter < 3):
  r = GetRoutes(missing_links)
  UpdateGraph(r)
  missing_link_update()
  G_n_miss = nx.complete_graph(G).to_directed()
  G_n_miss = Update_G_n_miss(G_n_miss)
  # showGraph()
  evaluate_paths_n_routes(10)
  missing_links = FilterRankSelectMissingLinks()
  # pprint.pprint(missing_link_dict)
  # for key, value in sorted(missing_link_dict.items(), key=lambda x: x[1]["occ_freq"]):
  #   if(not value["transferable"]):
  #     print(key)
  for key, value in sorted(paths_dict.items(), key=lambda x: x[1]["path_length"]):
    if(value["transfer_threshold"]):
      print(f"{key}: {value}")
  print()
  
  # print("Missing links: ",missing_links)
  counter+=1
showGraph()

