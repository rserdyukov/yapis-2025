// runtime.c
// Набор функций, которые вызываются из сгенерированного LLVM IR.

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

#define INITIAL_CAPACITY 16

struct node {
    char* s;
};

struct arc {
    struct node* from;
    struct node* to;
};

struct graph {
    struct node** nodes;
    int nodeCount;
    int nodeCapacity;

    struct arc** arcs;
    int arcCount;
    int arcCapacity;
};

static char* str_dup(const char* s) {
    if (!s) return NULL;
    size_t l = strlen(s);
    char* r = malloc(l + 1);
    memcpy(r, s, l + 1);
    return r;
}

char* read() {
    char* buffer = malloc(256);
    if (!buffer) return NULL;
    if (fgets(buffer, 256, stdin) == NULL) {
        free(buffer);
        return NULL;
    }
    size_t len = strlen(buffer);
    if (len > 0 && buffer[len-1] == '\n') {
        buffer[len-1] = '\0';
    }
    return buffer;
}

char* concatString(char* a, char* b) {
    if (!a) a = "";
    if (!b) b = "";
    size_t la = strlen(a), lb = strlen(b);
    char* r = malloc(la + lb + 1);
    memcpy(r, a, la);
    memcpy(r + la, b, lb);
    r[la + lb] = '\0';
    return r;
}

char* subtractString(char* a, char* b) {
    if (!a) return str_dup("");
    if (!b || b[0] == '\0') return str_dup(a);
    int la = (int)strlen(a);
    char* out = malloc(la + 1);
    int k = 0;
    for (int i = 0; i < la; ++i) {
        if (!strchr(b, a[i])) out[k++] = a[i];
    }
    out[k] = '\0';
    return out;
}

char* multiplyString(char* a, char* b) {
    if (!a) a = "";
    if (!b) b = "";
    int la = (int)strlen(a), lb = (int)strlen(b);
    char* out = malloc(la + lb + 1);
    int i = 0, j = 0, k = 0;
    while (i < la || j < lb) {
        if (i < la) out[k++] = a[i++];
        if (j < lb) out[k++] = b[j++];
    }
    out[k] = '\0';
    return out;
}

char* divideString(char* a, char* b) {
    return subtractString(a, b);
}

struct node* makeNode(char* s) {
    struct node* n = malloc(sizeof(struct node));
    n->s = str_dup(s ? s : "");
    return n;
}

void printBoolean(int b) {
    printf("%s\n", b ? "true" : "false");
}

void printStr(char* s) {
    if (!s) printf("(null)");
    else printf("%s", s);
}

void printNode(struct node* n) {
    if (!n) {
        printf("node(null)\n");
        return;
    }
    printf("node(%s)\n", n->s ? n->s : "null");
}

void printInt(int a) {
    printf("%d\n", a);
}

void printArc(struct arc* a) {
    if (!a) {
        printf("arc(null)\n");
        return;
    }
    printf("arc(%s->%s)\n", a->from ? (a->from->s ? a->from->s : "(null)") : "(null)",
                            a->to   ? (a->to  ->s ? a->to  ->s : "(null)") : "(null)");
}

void printGraph(struct graph* g) {
    if (!g) {
        printf("graph(null)\n");
        return;
    }

    printf("graph {\n");

    printf("  nodes: [");
    for (int i = 0; i < g->nodeCount; ++i) {
        printf("\"%s\"", g->nodes[i]->s ? g->nodes[i]->s : "(null)");
        if (i < g->nodeCount - 1) printf(", ");
    }
    printf("]\n");

    printf("  arcs: [");
    for (int i = 0; i < g->arcCount; ++i) {
        printf("(%s->%s)",
            g->arcs[i]->from ? g->arcs[i]->from->s : "(null)",
            g->arcs[i]->to   ? g->arcs[i]->to->s   : "(null)");
        if (i < g->arcCount - 1) printf(", ");
    }
    printf("]\n");

    printf("}\n");
}


struct node* nodeAdd(struct node* a, struct node* b) {
    if (!a && !b) return makeNode("");
    if (!a) return makeNode(b->s);
    if (!b) return makeNode(a->s);
    char* s = concatString(a->s, b->s);
    struct node* r = makeNode(s);
    free(s);
    return r;
}

struct node* nodeSub(struct node* a, struct node* b) {
    if (!a) return makeNode("");
    if (!b) return makeNode(a->s);
    char* s = subtractString(a->s, b->s);
    struct node* r = makeNode(s);
    free(s);
    return r;
}

struct node* nodeMul(struct node* a, struct node* b) {
    if (!a && !b) return makeNode("");
    if (!a) return makeNode(b->s);
    if (!b) return makeNode(a->s);
    char* s = multiplyString(a->s, b->s);
    struct node* r = makeNode(s);
    free(s);
    return r;
}

struct node* nodeDiv(struct node* a, struct node* b) {
    if (!a) return makeNode("");
    if (!b) return makeNode(a->s);
    char* s = divideString(a->s, b->s);
    struct node* r = makeNode(s);
    free(s);
    return r;
}

struct arc* makeArc(struct node* f, struct node* t) {
    struct arc* a = malloc(sizeof(struct arc));
    a->from = f;
    a->to = t;
    return a;
}

struct arc* arcAdd(struct arc* a, struct arc* b) {
    struct arc* r = malloc(sizeof(struct arc));
    r->from = nodeAdd(a->from, b->from);
    r->to   = nodeAdd(a->to,   b->to);
    return r;
}

struct arc* arcSub(struct arc* a, struct arc* b) {
    struct arc* r = malloc(sizeof(struct arc));
    r->from = nodeSub(a->from, b->from);
    r->to   = nodeSub(a->to,   b->to);
    return r;
}

struct arc* arcMul(struct arc* a, struct arc* b) {
    struct arc* r = malloc(sizeof(struct arc));
    r->from = nodeMul(a->from, b->from);
    r->to   = nodeMul(a->to,   b->to);
    return r;
}

struct arc* arcDiv(struct arc* a, struct arc* b) {
    struct arc* r = malloc(sizeof(struct arc));
    r->from = nodeDiv(a->from, b->from);
    r->to   = nodeDiv(a->to,   b->to);
    return r;
}

static struct graph* allocGraphWithCapacity(int nc, int ac) {
    struct graph* g = malloc(sizeof(struct graph));
    g->nodeCapacity = nc > 0 ? nc : INITIAL_CAPACITY;
    g->nodes = malloc(sizeof(struct node*) * g->nodeCapacity);
    g->nodeCount = 0;
    g->arcCapacity = ac > 0 ? ac : INITIAL_CAPACITY;
    g->arcs = malloc(sizeof(struct arc*) * g->arcCapacity);
    g->arcCount = 0;
    return g;
}

struct graph* makeGraph() {
    return allocGraphWithCapacity(INITIAL_CAPACITY, INITIAL_CAPACITY);
}

struct graph* mkGraph(struct node* n, struct arc* a) {
    struct graph* g = makeGraph();
    if (n) {
        if (g->nodeCount >= g->nodeCapacity) {
            g->nodeCapacity *= 2;
            g->nodes = realloc(g->nodes, sizeof(struct node*) * g->nodeCapacity);
        }
        g->nodes[g->nodeCount++] = n;
    }
    if (a) {
        if (g->arcCount >= g->arcCapacity) {
            g->arcCapacity *= 2;
            g->arcs = realloc(g->arcs, sizeof(struct arc*) * g->arcCapacity);
        }
        g->arcs[g->arcCount++] = a;
    }
    return g;
}

struct graph* copyGraphShallow(struct graph* s) {
    struct graph* g = makeGraph();
    for (int i = 0; i < s->nodeCount; ++i) {
        if (g->nodeCount >= g->nodeCapacity) {
            g->nodeCapacity *= 2;
            g->nodes = realloc(g->nodes, sizeof(struct node*) * g->nodeCapacity);
        }
        g->nodes[g->nodeCount++] = s->nodes[i];
    }
    for (int i = 0; i < s->arcCount; ++i) {
        if (g->arcCount >= g->arcCapacity) {
            g->arcCapacity *= 2;
            g->arcs = realloc(g->arcs, sizeof(struct arc*) * g->arcCapacity);
        }
        g->arcs[g->arcCount++] = s->arcs[i];
    }
    return g;
}

struct graph* addNode(struct graph* g, struct node* n) {
    if (!g) g = makeGraph();
    if (g->nodeCount >= g->nodeCapacity) {
        g->nodeCapacity *= 2;
        g->nodes = realloc(g->nodes, sizeof(struct node*) * g->nodeCapacity);
    }
    g->nodes[g->nodeCount++] = n;
    return g;
}

struct graph* deleteNode(struct graph* g, struct node* n) {
    if (!g || !n) return g;
    int w = 0;
    for (int i = 0; i < g->nodeCount; ++i) {
        if (strcmp(g->nodes[i]->s, n->s) != 0) {
            g->nodes[w++] = g->nodes[i];
        }
    }
    g->nodeCount = w;
    w = 0;
    for (int i = 0; i < g->arcCount; ++i) {
        if (strcmp(g->arcs[i]->from->s, n->s) != 0 && strcmp(g->arcs[i]->to->s, n->s) != 0) {
            g->arcs[w++] = g->arcs[i];
        }
    }
    g->arcCount = w;
    return g;
}

struct graph* addArc(struct graph* g, struct arc* a) {
    if (!g) g = makeGraph();
    if (g->arcCount >= g->arcCapacity) {
        g->arcCapacity *= 2;
        g->arcs = realloc(g->arcs, sizeof(struct arc*) * g->arcCapacity);
    }
    g->arcs[g->arcCount++] = a;
    return g;
}

struct graph* deleteArc(struct graph* g, struct arc* a) {
    if (!g || !a) return g;
    int w = 0;
    for (int i = 0; i < g->arcCount; ++i) {
        if (!(strcmp(g->arcs[i]->from->s, a->from->s) == 0 &&
              strcmp(g->arcs[i]->to  ->s, a->to  ->s) == 0)) {
            g->arcs[w++] = g->arcs[i];
        }
    }
    g->arcCount = w;
    return g;
}

struct node* getNode(struct graph* g, int idx) {
    if (!g) return NULL;
    if (idx < 0 || idx >= g->nodeCount) return NULL;
    return g->nodes[idx];
}

struct node* getNeighbour(struct graph* g, struct node* n, int idx) {
    if (!g || !n) return NULL;
    int found = 0;
    for (int i = 0; i < g->arcCount; ++i) {
        if (strcmp(g->arcs[i]->from->s, n->s) == 0) {
            if (found == idx) return g->arcs[i]->to;
            found++;
        }
    }
    return NULL;
}

int hasNode(struct graph* g, struct node* n) {
    if (!g || !n) return 0;
    for (int i = 0; i < g->nodeCount; ++i) {
        if (strcmp(g->nodes[i]->s, n->s) == 0) return 1;
    }
    return 0;
}

int hasArc(struct graph* g, struct arc* a) {
    if (!g || !a) return 0;
    for (int i = 0; i < g->arcCount; ++i) {
        if (strcmp(g->arcs[i]->from->s, a->from->s) == 0 &&
            strcmp(g->arcs[i]->to  ->s, a->to  ->s) == 0) return 1;
    }
    return 0;
}

int size(struct graph* g) {
    if (!g) return 0;
    return g->nodeCount;
}


struct graph* graphAdd(struct graph* a, struct graph* b) {
    if (!a) return copyGraphShallow(b);
    if (!b) return copyGraphShallow(a);
    struct graph* g = copyGraphShallow(a);
    for (int i = 0; i < b->nodeCount; ++i) g = addNode(g, b->nodes[i]);
    for (int i = 0; i < b->arcCount; ++i) g = addArc(g, b->arcs[i]);
    return g;
}

struct graph* graphSub(struct graph* a, struct graph* b) {
    if (!a) return makeGraph();
    if (!b) return copyGraphShallow(a);
    return deleteNode(copyGraphShallow(a), NULL), (deleteArc(copyGraphShallow(a), NULL), copyGraphShallow(a)); 
}

struct graph* graphSub_proper(struct graph* a, struct graph* b) {
    if (!a) return makeGraph();
    if (!b) return copyGraphShallow(a);
    struct graph* g = makeGraph();
    for (int i = 0; i < a->nodeCount; ++i) {
        int found = 0;
        for (int j = 0; j < b->nodeCount; ++j) {
            if (strcmp(a->nodes[i]->s, b->nodes[j]->s) == 0) { found = 1; break; }
        }
        if (!found) addNode(g, a->nodes[i]);
    }
    for (int i = 0; i < a->arcCount; ++i) {
        int found = 0;
        for (int j = 0; j < b->arcCount; ++j) {
            if (strcmp(a->arcs[i]->from->s, b->arcs[j]->from->s) == 0 &&
                strcmp(a->arcs[i]->to  ->s, b->arcs[j]->to  ->s) == 0) { found = 1; break; }
        }
        if (!found) addArc(g, a->arcs[i]);
    }
    return g;
}

struct graph* graphMul(struct graph* a, struct graph* b) {
    if (!a || !b) return makeGraph();
    struct graph* g = makeGraph();
    for (int i = 0; i < a->nodeCount; ++i)
        for (int j = 0; j < b->nodeCount; ++j)
            addNode(g, nodeAdd(a->nodes[i], b->nodes[j]));

    for (int i = 0; i < a->arcCount; ++i)
        for (int j = 0; j < b->arcCount; ++j)
            addArc(g, arcAdd(a->arcs[i], b->arcs[j]));

    return g;
}

struct graph* graphDiv(struct graph* a, struct graph* b) {
    return graphSub_proper(a, b);
}

struct node* concatNode(struct node* a, struct node* b) { return nodeAdd(a, b); }
struct arc*  concatArc(struct arc* a, struct arc* b)   { return arcAdd(a, b); }
struct graph* concatGraph(struct graph* a, struct graph* b) { return graphAdd(a, b); }

int stringEq(char* a, char* b) {
    if (!a || !b) return 0;
    return strcmp(a, b) == 0;
}

int stringNeq(char* a, char* b) {
    return !stringEq(a, b);
}

int nodeEq(struct node* a, struct node* b) {
    if (!a || !b) return 0;
    if (!a->s || !b->s) return 0;
    return strcmp(a->s, b->s) == 0;
}

int nodeNeq(struct node* a, struct node* b) {
    return !nodeEq(a, b);
}

int arcEq(struct arc* a, struct arc* b) {
    if (!a || !b) return 0;
    return nodeEq(a->from, b->from) && nodeEq(a->to, b->to);
}

int arcNeq(struct arc* a, struct arc* b) {
    return !arcEq(a, b);
}

int graphEq(struct graph* a, struct graph* b) {
    if (!a || !b) return 0;
    if (a->nodeCount != b->nodeCount || a->arcCount != b->arcCount) return 0;
    for (int i = 0; i < a->nodeCount; ++i) {
        if (strcmp(a->nodes[i]->s, b->nodes[i]->s) != 0) return 0;
    }
    for (int i = 0; i < a->arcCount; ++i) {
        if (strcmp(a->arcs[i]->from->s, b->arcs[i]->from->s) != 0) return 0;
        if (strcmp(a->arcs[i]->to  ->s, b->arcs[i]->to  ->s) != 0) return 0;
    }
    return 1;
}

int graphNeq(struct graph* g1, struct graph* g2) {
    return !graphEq(g1, g2);
}


struct arc* mkArc_alias(struct node* f, struct node* t) { return makeArc(f, t); }
struct graph* mkGraph_alias(struct node* n, struct arc* a) { return makeGraph(n, a); }

struct node* castStringToNode(char* s) {
    return makeNode(s);
}

struct arc* castNodeToArc(struct node* n) {
    if (!n) return NULL;
    return makeArc(n, n);
}

struct graph* castArcToGraph(struct arc* a) {
    return makeGraph(NULL, a);
}

int castStringToInt(char* s) {
    if (!s) return 0;
    return atoi(s);
}

char* castIntToString(int x) {
    char* buffer = malloc(12);
    if (!buffer) return NULL;
    sprintf(buffer, "%d", x);
    return buffer;
}

struct graph* shortestPath(struct graph* g, struct node* start, struct node* end) {
    if (!g || !start || !end) return makeGraph();

    int n = g->nodeCount;
    if (n == 0) return makeGraph();

    int startIdx = -1, endIdx = -1;
    for (int i = 0; i < n; ++i) {
        if (nodeEq(g->nodes[i], start)) startIdx = i;
        if (nodeEq(g->nodes[i], end))   endIdx = i;
    }
    if (startIdx == -1 || endIdx == -1) return makeGraph();

    int* prev = malloc(sizeof(int) * n);
    for (int i = 0; i < n; ++i) prev[i] = -1;

    int* queue = malloc(sizeof(int) * n);
    int qStart = 0, qEnd = 0;
    int* visited = malloc(sizeof(int) * n);
    for (int i = 0; i < n; ++i) visited[i] = 0;

    queue[qEnd++] = startIdx;
    visited[startIdx] = 1;

    while (qStart < qEnd) {
        int u = queue[qStart++];
        for (int i = 0; i < g->arcCount; ++i) {
            if (strcmp(g->arcs[i]->from->s, g->nodes[u]->s) == 0) {
                struct node* vNode = g->arcs[i]->to;
                int vIdx = -1;
                for (int j = 0; j < n; ++j) {
                    if (nodeEq(g->nodes[j], vNode)) { vIdx = j; break; }
                }
                if (vIdx != -1 && !visited[vIdx]) {
                    visited[vIdx] = 1;
                    prev[vIdx] = u;
                    queue[qEnd++] = vIdx;
                }
            }
        }
    }

    if (!visited[endIdx]) {
        free(prev); free(queue); free(visited);
        return makeGraph();
    }

    struct graph* path = makeGraph();
    int idx = endIdx;
    while (idx != -1) {
        addNode(path, g->nodes[idx]);
        idx = prev[idx];
    }

    for (int i = 0, j = path->nodeCount - 1; i < j; ++i, --j) {
        struct node* tmp = path->nodes[i];
        path->nodes[i] = path->nodes[j];
        path->nodes[j] = tmp;
    }

    for (int i = 0; i < path->nodeCount - 1; ++i) {
        addArc(path, makeArc(path->nodes[i], path->nodes[i + 1]));
    }

    free(prev); free(queue); free(visited);
    return path;
}

struct graph* bfs(struct graph* g, struct node* start) {
    if (!g || !start) return makeGraph();

    int n = g->nodeCount;
    if (n == 0) return makeGraph();

    int startIdx = -1;
    for (int i = 0; i < n; ++i) {
        if (nodeEq(g->nodes[i], start)) {
            startIdx = i;
            break;
        }
    }
    if (startIdx == -1) return makeGraph();

    int* visited = malloc(sizeof(int) * n);
    for (int i = 0; i < n; ++i) visited[i] = 0;

    int* queue = malloc(sizeof(int) * n);
    int qStart = 0, qEnd = 0;

    struct graph* result = makeGraph();

    queue[qEnd++] = startIdx;
    visited[startIdx] = 1;
    addNode(result, g->nodes[startIdx]);

    while (qStart < qEnd) {
        int u = queue[qStart++];
        struct node* uNode = g->nodes[u];

        for (int i = 0; i < g->arcCount; ++i) {
            struct arc* a = g->arcs[i];
            if (nodeEq(a->from, uNode)) {
                addArc(result, a);

                int vIdx = -1;
                for (int j = 0; j < n; ++j) {
                    if (nodeEq(g->nodes[j], a->to)) {
                        vIdx = j;
                        break;
                    }
                }

                if (vIdx != -1 && !visited[vIdx]) {
                    visited[vIdx] = 1;
                    queue[qEnd++] = vIdx;
                    addNode(result, g->nodes[vIdx]);
                }
            }
        }
    }

    free(visited);
    free(queue);
    return result;
}

struct graph* dfs(struct graph* g, struct node* start) {
    if (!g || !start) return makeGraph();

    int n = g->nodeCount;
    if (n == 0) return makeGraph();

    int startIdx = -1;
    for (int i = 0; i < n; ++i) {
        if (nodeEq(g->nodes[i], start)) {
            startIdx = i;
            break;
        }
    }
    if (startIdx == -1) return makeGraph();
    int* visited = malloc(sizeof(int) * n);
    for (int i = 0; i < n; ++i) visited[i] = 0;

    int* stack = malloc(sizeof(int) * n);
    int sp = 0;

    struct graph* result = makeGraph();

    stack[sp++] = startIdx;

    while (sp > 0) {
        int u = stack[--sp];
        if (visited[u]) continue;
        visited[u] = 1;

        struct node* uNode = g->nodes[u];
        addNode(result, uNode);

        for (int i = g->arcCount - 1; i >= 0; --i) {
            struct arc* a = g->arcs[i];
            if (nodeEq(a->from, uNode)) {
                addArc(result, a);

                int vIdx = -1;
                for (int j = 0; j < n; ++j) {
                    if (nodeEq(g->nodes[j], a->to)) {
                        vIdx = j;
                        break;
                    }
                }

                if (vIdx != -1 && !visited[vIdx]) {
                    stack[sp++] = vIdx;
                }
            }
        }
    }
    free(visited);
    free(stack);
    return result;
}

