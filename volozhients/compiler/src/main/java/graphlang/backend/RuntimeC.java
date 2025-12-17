package graphlang.backend;

public final class RuntimeC {
    public static final String RUNTIME_C_HEADER = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int from;
    int to;
} Arc;

typedef struct {
    int *nodes;
    int nodesCount;
    int nodesCapacity;
    Arc *arcs;
    int arcsCount;
    int arcsCapacity;
} Graph;

/* node registry: map id -> name (id starts from 1) */
static int __node_counter = 1;
static char **__node_names = NULL;
static int __node_names_capacity = 0;

/* ensure capacity for __node_names up to index id (inclusive) */
static void ensure_node_names_capacity(int id) {
    if (id <= 0) return;
    if (__node_names_capacity < id + 1) {
        int newCap = (__node_names_capacity == 0) ? 8 : __node_names_capacity * 2;
        while (newCap < id + 1) newCap *= 2;
        __node_names = (char**)realloc(__node_names, sizeof(char*) * newCap);
        for (int i = __node_names_capacity; i < newCap; ++i) __node_names[i] = NULL;
        __node_names_capacity = newCap;
    }
}

int node_create(const char* name) {
    int id = __node_counter++;
    ensure_node_names_capacity(id);
    if (name) {
        __node_names[id] = strdup(name);
    } else {
        __node_names[id] = NULL;
    }
    return id;
}

Graph* graph_create() {
    Graph* g = (Graph*)malloc(sizeof(Graph));
    g->nodes = NULL;
    g->nodesCount = 0;
    g->nodesCapacity = 0;
    g->arcs = NULL;
    g->arcsCount = 0;
    g->arcsCapacity = 0;
    return g;
}

static void ensure_nodes_capacity(Graph* g, int extra) {
    if (g->nodesCapacity < g->nodesCount + extra) {
        int newCap = (g->nodesCapacity == 0) ? 4 : g->nodesCapacity * 2;
        while (newCap < g->nodesCount + extra) newCap *= 2;
        g->nodes = (int*)realloc(g->nodes, sizeof(int) * newCap);
        g->nodesCapacity = newCap;
    }
}
static void ensure_arcs_capacity(Graph* g, int extra) {
    if (g->arcsCapacity < g->arcsCount + extra) {
        int newCap = (g->arcsCapacity == 0) ? 4 : g->arcsCapacity * 2;
        while (newCap < g->arcsCount + extra) newCap *= 2;
        g->arcs = (Arc*)realloc(g->arcs, sizeof(Arc) * newCap);
        g->arcsCapacity = newCap;
    }
}

Graph* graph_add_node(Graph* g, int node) {
    ensure_nodes_capacity(g, 1);
    g->nodes[g->nodesCount++] = node;
    return g;
}

Graph* graph_remove_node(Graph* g, int node) {
    int j = 0;
    for (int i = 0; i < g->nodesCount; ++i) {
        if (g->nodes[i] != node) {
            g->nodes[j++] = g->nodes[i];
        }
    }
    g->nodesCount = j;

    int k = 0;
    for (int i = 0; i < g->arcsCount; ++i) {
        if (!(g->arcs[i].from == node || g->arcs[i].to == node)) {
            g->arcs[k++] = g->arcs[i];
        }
    }
    g->arcsCount = k;

    return g;
}

Graph* graph_add_nodes(Graph* g, int* nodes, int count) {
    ensure_nodes_capacity(g, count);
    for (int i = 0; i < count; ++i) {
        g->nodes[g->nodesCount++] = nodes[i];
    }
    return g;
}

Graph* graph_add_arc(Graph* g, Arc arc) {
    ensure_arcs_capacity(g, 1);
    g->arcs[g->arcsCount++] = arc;
    return g;
}

Graph* graph_remove_arc(Graph* g, Arc arc) {
    int j = 0;
    for (int i = 0; i < g->arcsCount; ++i) {
        if (!(g->arcs[i].from == arc.from && g->arcs[i].to == arc.to)) {
            g->arcs[j++] = g->arcs[i];
        }
    }
    g->arcsCount = j;
    return g;
}

int graph_has_node(Graph* g, int node) {
    for (int i = 0; i < g->nodesCount; ++i) {
        if (g->nodes[i] == node) return 1;
    }
    return 0;
}

int* graph_get_nodes(Graph* g, int* outCount) {
    *outCount = g->nodesCount;
    int* arr = (int*)malloc(sizeof(int) * g->nodesCount);
    for (int i = 0; i < g->nodesCount; ++i) arr[i] = g->nodes[i];
    return arr;
}

Arc arc_create(int from, int to) {
    Arc a;
    a.from = from;
    a.to = to;
    return a;
}

/* BFS/DFS: implementations */

/* BFS: prints visited nodes (names) as side effect */
void BFS(Graph* g, int start) {
    if (!g) return;
    if (start <= 0 || __node_names_capacity == 0) return;

    int maxId = __node_names_capacity;
    char *visited = (char*)calloc(maxId, 1);
    int *queue = (int*)malloc(sizeof(int) * (g->nodesCount > 0 ? g->nodesCount : 1));
    int qh = 0, qt = 0;

    if (graph_has_node(g, start)) {
        visited[start] = 1;
        queue[qt++] = start;
    }

    while (qh < qt) {
        int cur = queue[qh++];
        if (cur > 0 && cur < __node_names_capacity && __node_names[cur]) {
            printf("%s\\n", __node_names[cur]);
        } else {
            printf("%d\\n", cur);
        }
        for (int i = 0; i < g->arcsCount; ++i) {
            if (g->arcs[i].from == cur) {
                int to = g->arcs[i].to;
                if (to > 0 && to < maxId && !visited[to]) {
                    visited[to] = 1;
                    queue[qt++] = to;
                }
            }
        }
    }

    free(queue);
    free(visited);
}

/* DFS: prints visited nodes (names) as side effect */
void DFS(Graph* g, int start) {
    if (!g) return;
    if (start <= 0 || __node_names_capacity == 0) return;

    int maxId = __node_names_capacity;
    char *visited = (char*)calloc(maxId, 1);
    int *stack = (int*)malloc(sizeof(int) * (g->nodesCount > 0 ? g->nodesCount : 1));
    int sp = 0;

    if (graph_has_node(g, start)) {
        visited[start] = 1;
        stack[sp++] = start;
    }

    while (sp > 0) {
        int cur = stack[--sp];
        if (cur > 0 && cur < __node_names_capacity && __node_names[cur]) {
            printf("%s\\n", __node_names[cur]);
        } else {
            printf("%d\\n", cur);
        }
        for (int i = g->arcsCount - 1; i >= 0; --i) {
            if (g->arcs[i].from == cur) {
                int to = g->arcs[i].to;
                if (to > 0 && to < maxId && !visited[to]) {
                    visited[to] = 1;
                    stack[sp++] = to;
                }
            }
        }
    }

    free(stack);
    free(visited);
}

/* BFS_nodes: returns array of visited node ids (caller must free), sets *outCount */
int* BFS_nodes(Graph* g, int start, int* outCount) {
    if (!g || outCount == NULL) return NULL;
    *outCount = 0;
    if (!graph_has_node(g, start)) return NULL;

    int maxId = __node_names_capacity;
    char *visited = (char*)calloc(maxId, 1);
    int *queue = (int*)malloc(sizeof(int) * (g->nodesCount > 0 ? g->nodesCount : 1));
    int qh = 0, qt = 0;

    visited[start] = 1;
    queue[qt++] = start;

    int *result = (int*)malloc(sizeof(int) * (g->nodesCount > 0 ? g->nodesCount : 1));
    int rc = 0;

    while (qh < qt) {
        int cur = queue[qh++];
        result[rc++] = cur;
        for (int i = 0; i < g->arcsCount; ++i) {
            if (g->arcs[i].from == cur) {
                int to = g->arcs[i].to;
                if (to > 0 && to < maxId && !visited[to]) {
                    visited[to] = 1;
                    queue[qt++] = to;
                }
            }
        }
    }

    free(queue);
    free(visited);

    *outCount = rc;
    return result;
}

/* DFS_nodes: returns array of visited node ids (caller must free), sets *outCount */
int* DFS_nodes(Graph* g, int start, int* outCount) {
    if (!g || outCount == NULL) return NULL;
    *outCount = 0;
    if (!graph_has_node(g, start)) return NULL;

    int maxId = __node_names_capacity;
    char *visited = (char*)calloc(maxId, 1);
    int *stack = (int*)malloc(sizeof(int) * (g->nodesCount > 0 ? g->nodesCount : 1));
    int sp = 0;

    int *result = (int*)malloc(sizeof(int) * (g->nodesCount > 0 ? g->nodesCount : 1));
    int rc = 0;

    visited[start] = 1;
    stack[sp++] = start;

    while (sp > 0) {
        int cur = stack[--sp];
        result[rc++] = cur;
        for (int i = g->arcsCount - 1; i >= 0; --i) {
            if (g->arcs[i].from == cur) {
                int to = g->arcs[i].to;
                if (to > 0 && to < maxId && !visited[to]) {
                    visited[to] = 1;
                    stack[sp++] = to;
                }
            }
        }
    }

    free(stack);
    free(visited);

    *outCount = rc;
    return result;
}

/* printing / string utilities */
void print_str(char* s) {
    if (s) {
        printf("%s", s);
    } else {
        printf("(null)\\n");
    }
}
void print_any(void* p) {
    printf("%p", p);
}
char* str_concat(char* a, char* b) {
    if (!a) return b ? strdup(b) : NULL;
    if (!b) return strdup(a);
    size_t la = strlen(a);
    size_t lb = strlen(b);
    char* r = (char*)malloc(la + lb + 1);
    memcpy(r, a, la);
    memcpy(r + la, b, lb);
    r[la + lb] = '\\0';
    return r;
}

/* Print a node by id, preferring the name registered at creation time */
void print_node_name(int id) {
    if (id > 0 && id < __node_names_capacity && __node_names[id]) {
        printf("%s", __node_names[id]);
    } else {
        printf("%d", id);
    }
}

/* Print an arc value: use names of endpoints if available */
void print_arc(Arc a) {
    const char* fromName = NULL;
    const char* toName = NULL;
    if (a.from > 0 && a.from < __node_names_capacity) fromName = __node_names[a.from];
    if (a.to > 0 && a.to < __node_names_capacity) toName = __node_names[a.to];
    if (fromName && toName) {
        printf("<%s,%s>", fromName, toName);
    } else {
        printf("<%d,%d>", a.from, a.to);
    }
}

/* Print node group (array of node ids) as names when possible */
void print_node_group(int* nodes, int count) {
    if (!nodes || count <= 0) {
        printf("()");
        return;
    }
    printf("(");
    for (int i = 0; i < count; ++i) {
        if (i) printf(",");
        int id = nodes[i];
        if (id > 0 && id < __node_names_capacity && __node_names[id]) {
            printf("%s", __node_names[id]);
        } else {
            printf("%d", id);
        }
    }
    printf(")");
}

/* Print a graph with node names and arc endpoints as names when available */
void print_graph(Graph* g) {
    if (!g) {
        printf("<null graph>");
        return;
    }
    /* Print nodes: try to use registered names */
    printf("Graph(nodes=");
    if (g->nodesCount == 0) {
        printf("()");
    } else {
        printf("(");
        for (int i = 0; i < g->nodesCount; ++i) {
            if (i) printf(",");
            int id = g->nodes[i];
            if (id > 0 && id < __node_names_capacity && __node_names[id]) {
                printf("%s", __node_names[id]);
            } else {
                printf("%d", id);
            }
        }
        printf(")");
    }
    /* Print arcs: endpoints by names if possible */
    printf(", arcs=");
    if (g->arcsCount == 0) {
        printf("()");
    } else {
        printf("(");
        for (int i = 0; i < g->arcsCount; ++i) {
            if (i) printf(",");
            Arc a = g->arcs[i];
            const char* fromName = NULL;
            const char* toName = NULL;
            if (a.from > 0 && a.from < __node_names_capacity) fromName = __node_names[a.from];
            if (a.to > 0 && a.to < __node_names_capacity) toName = __node_names[a.to];
            if (fromName && toName) {
                printf("<%s,%s>", fromName, toName);
            } else {
                printf("<%d,%d>", a.from, a.to);
            }
        }
        printf(")");
    }
    printf(")\\n");
}
""";
}
