from config import N,t
from collections import deque

def normalize_graph(matrix):
    for i in range(1,N+1):
        for i2 in range(1,N+1):
            matrix[i][i2]//=2
    return matrix

def complement_graph(graph):
    for i in range(1,N+1):
        for i2 in range(1,N+1):
            graph[i][i2]= 1-graph[i][i2]
    return graph

def find_maximum_matching(graph):
    match = [0] * (N + 1)
    base = [i for i in range(N + 1)]
    p = [0] * (N + 1)
    q = deque()
    used = [False] * (N + 1)
    
    def lca(a, b):
        visited = [False] * (N + 1)
        while True:
            a = base[a]
            visited[a] = True
            if match[a] == 0:
                break
            a = p[match[a]]
        while True:
            b = base[b]
            if visited[b]:
                return b
            if match[b] == 0:
                break
            b = p[match[b]]
        return 0

    def mark_blossom(a, b, l, S):
        while base[a] != l:
            S[base[a]] = S[base[match[a]]] = True
            p[a] = b
            b = match[a]
            a = p[match[a]]
    
    def find_path(start):
        S = [False] * (N + 1)
        p[:] = [0] * (N + 1)
        for i in range(1, N + 1):
            base[i] = i
        q.clear()
        q.append(start)
        used[:] = [False] * (N + 1)
        used[start] = True
        
        while q:
            v = q.popleft()
            for u in range(1, N + 1):
                if graph[v][u] and base[v] != base[u] and match[v] != u:
                    if (u == start) or (match[u] != 0 and p[match[u]] != 0):
                        l = lca(v, u)
                        S = [False] * (N + 1)
                        mark_blossom(v, u, l, S)
                        mark_blossom(u, v, l, S)
                        for i in range(1, N + 1):
                            if S[base[i]]:
                                base[i] = l
                                if not used[i]:
                                    used[i] = True
                                    q.append(i)
                    elif p[u] == 0:
                        p[u] = v
                        if match[u] == 0:
                            # Augmenting path found
                            while u != 0:
                                v = p[u]
                                w = match[v]
                                match[v] = u
                                match[u] = v
                                u = w
                            return True
                        u = match[u]
                        used[u] = True
                        q.append(u)
        return False

    for i in range(1, N + 1):
        if match[i] == 0:
            find_path(i)

    S=set()
    M=set()
    for i in range(1, N + 1):
        if match[i] != 0 and i < match[i]:
            S.add(i)
            S.add(match[i])
            M.add((i,match[i]))
    return S,M

def find_triangle_heads(graph,S,M):
    compl=complement_graph(graph)
    T=set()
    for edge in M:
        for i in S:
            if compl[i][edge[0]]==1 and compl[i][edge[1]]==1:
                T.add(i)
    return T



def find_star(graph):
    graph = normalize_graph(graph)
    complement = complement_graph(graph)
    S,M = find_maximum_matching(complement)
    T = find_triangle_heads(graph,S,M)
    C = set([i for i in range(1,N+1) if i not in S.union(T)])
    D = set()
    for i in range(1,N+1):
        if all([graph[i][i2]==1 for i2 in C]):
            D.add(i)
    G = set()
    for i in range(1,N+1):
        if sum([graph[i][i2] or i==i2 for i2 in C])>=2*t+1:
            G.add(i)
    F = set()
    for i in range(1,N+1):
        if sum([graph[i][i2] or i==i2 for i2 in G])>=3*t+1:
            F.add(i)
    if len(C)>=2*t+1 and C.issubset(D) and len(D)>=3*t+1 and len(G)>=3*t+1 and len(F)>=3*t+1:
        return C,D,G,F
    else:
        return False

def verify_star(graph,C,D,G,F):
    graph = normalize_graph(graph)
    if len(C)<2*t+1 or not C.issubset(D) or len(D)<3*t+1 or len(G)<3*t+1 or len(F)<3*t+1:
        return False
    realG = set()
    for i in range(1,N+1):
        if sum([graph[i][i2] or i==i2 for i2 in C])>=2*t+1:
            realG.add(i)
    realF = set()
    for i in range(1,N+1):
        if sum([graph[i][i2] or i==i2 for i2 in G])>=3*t+1:
            realF.add(i)
    if not G.issubset(realG) or not F.issubset(realF):
        return False
    for d in D:
        if any([graph[d][c]==0 for c in C if c!=d]):
            return False
    return True


