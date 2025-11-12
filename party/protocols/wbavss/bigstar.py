from config import N,t
from .star import find_star

def normalize_graph(matrix):
    res=[[0 for i in range(N+1)] for i2 in range(N+1)]
    for i in range(1,N+1):
        for i2 in range(1,N+1):
            res[i][i2]=matrix[i][i2]//2
    return res

def complement_graph(graph):
    res=[[0 for i in range(N+1)] for i2 in range(N+1)]
    for i in range(1,N+1):
        for i2 in range(1,N+1):
            res[i][i2]= 1-graph[i][i2]
    return res

def find_dense_or_bigstar(graph):
    graph = normalize_graph(graph)
    C = set()
    for i in range(1,N+1):
        if sum([graph[i][i2] or i==i2 for i2 in range(1,N+1)])>=N-t+t//2+1:
            C.add(i)
    if len(C)>=N-t:
        return "dense",C,set()
    C_inv=set([i for i in range(1,N+1) if i not in C])
    for i in C_inv:
        GAMMA_SET=set([j for j in range(1,N+1) if graph[i][j] or i==j])
        addme=1
        while len(GAMMA_SET)<N-t+t//2:
            GAMMA_SET.add(addme)
            addme+=1
        GAMMA=list(GAMMA_SET)
        GAMMA_inv={}
        for ind,g in enumerate(GAMMA):
            GAMMA_inv[g]=ind
        N_GAMMA=len(GAMMA)
        G_GAMMA=[[0 for j in range(N_GAMMA+1)] for j2 in range(N_GAMMA+1)]
        for j in range(N+1):
            for j2 in range(N+1):
                if j in GAMMA_SET and j2 in GAMMA_SET:
                    G_GAMMA[GAMMA_inv[j]][GAMMA_inv[j2]]=graph[j][j2]
                    G_GAMMA[GAMMA_inv[j2]][GAMMA_inv[j]]=graph[j2][j]
        star=find_star(G_GAMMA,N_GAMMA,t//2)
        if star:
            C,D=star
            return "bigstar",C,D
    return None


def verify_dense_or_bigstar(graph,kind,C,D):
    graph = normalize_graph(graph)
    if kind=="dense":
        if len(C)<N-t:
            return False
        for i in C:
            if sum([graph[i][i2] or i==i2 for i2 in range(1,N+1)])<N-t+t//2:
                return False
        return True
    if kind=="bigstar":
        if len(C)<N-2*t+t//2 or len(D)<N-t or not C.issubset(D):
            return False
        for d in D:
            if any([graph[d][c]==0 for c in C if c!=d]):
                return False
        return True
    return False


