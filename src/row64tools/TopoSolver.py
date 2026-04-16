'''
From:
https://github.com/bhavinjawade/Advanced-Data-Structures-with-Python/blob/master/Kahns_Algorithm_Topologicalsort/Kahns_Algo_Topologicalsort.py

MIT License

Copyright (c) 2017 Bhavin Jawade

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from collections import defaultdict

class TopoSolver: 
  def __init__(self,size):
        self.graph = defaultdict(list)
        self.vert = size

  def add_edge(self,a,b):
    a = int(a)
    b = int(b)
    self.graph[b].append(a)
  
  def log_graph(self):
    print(self.graph)
  
  def topo_sort(self):
    indegree = [0]*self.vert
    for i in self.graph:
      for j in self.graph[i]:
        indegree[j] += 1
    store = []
    for i in range(self.vert):
      if indegree[i] == 0:
        store.append(i)
    visit = 0
    topsort = []
    while store:
      u = store.pop(0)
      topsort.append(u)
      for j in self.graph[u]:
        indegree[j] -= 1
        if(indegree[j] == 0):
          store.append(j)
      visit += 1
    if(visit != self.vert):print("Dependency Graph Cycle Detected")
    return topsort[::-1]

    