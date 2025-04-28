#include <bits/stdc++.h>
using namespace std;

const double EPS = 1e-9;

struct Point {
    double x, y;
    bool operator<(const Point& other) const {
        if (fabs(x - other.x) < EPS) return y < other.y;
        return x < other.x;
    }
};

struct Line {
    double a, b;
    int id;

    double getY(double x) const {
        return a * x + b;
    }

    bool operator==(const Line& other) const {
        return fabs(a - other.a) < EPS && fabs(b - other.b) < EPS;
    }
};

Point getIntersection(const Line& l1, const Line& l2) {
    double x = (l2.b - l1.b) / (l1.a - l2.a);
    double y = l1.a * x + l1.b;
    return {x, y};
}

double triangleArea(const Point& a, const Point& b, const Point& c) {
    return fabs((a.x * (b.y - c.y) +
                 b.x * (c.y - a.y) +
                 c.x * (a.y - b.y)) / 2.0);
}

bool isDistinct(int a, int b, int c) {
    return a != b && b != c && a != c;
}

struct ListNode {
    Line* line;
    int id;
    ListNode* prev = nullptr;
    ListNode* next = nullptr;

    ListNode(Line* l) : line(l), id(l->id) {}
};

class LinkedList {
public:
    ListNode* head = nullptr;
    unordered_map<int, ListNode*> idMap;

    void build(const vector<Line>& sortedLines) {
        ListNode* prevNode = nullptr;
        for (const auto& line : sortedLines) {
            Line* lineCopy = new Line(line);
            ListNode* node = new ListNode(lineCopy);
            if (!head) head = node;
            node->prev = prevNode;
            if (prevNode) prevNode->next = node;
            prevNode = node;
            idMap[node->id] = node;
        }
    }

    void swapNodes(int id1, int id2) {
        if (id1 == id2) return;
        ListNode* n1 = idMap[id1];
        ListNode* n2 = idMap[id2];
        if (!n1 || !n2) return;
        if (n1 == n2) return;

        // Ensure n1 comes before n2 in the list
        ListNode* t = n1;
        while (t && t != n2) t = t->next;
        if (!t) swap(n1, n2); // n1 was after n2

        ListNode* p1 = n1->prev;
        ListNode* n1n = n1->next;
        ListNode* p2 = n2->prev;
        ListNode* n2n = n2->next;

        if (n1->next == n2) { // adjacent
            if (p1) p1->next = n2;
            n2->prev = p1;

            n2->next = n1;
            n1->prev = n2;

            n1->next = n2n;
            if (n2n) n2n->prev = n1;
        } else {
            if (p1) p1->next = n2;
            n2->prev = p1;
            n2->next = n1n;
            if (n1n) n1n->prev = n2;

            if (p2) p2->next = n1;
            n1->prev = p2;
            n1->next = n2n;
            if (n2n) n2n->prev = n1;
        }

        if (head == n1) head = n2;
        else if (head == n2) head = n1;
    }

    pair<int, int> getAdjacent(int id) {
        ListNode* node = idMap[id];
        int up = -1, down = -1;
        if (node->prev) up = node->prev->id;
        if (node->next) down = node->next->id;
        return {up, down};
    }

    ~LinkedList() {
        ListNode* curr = head;
        while (curr) {
            ListNode* tmp = curr;
            curr = curr->next;
            delete tmp->line;
            delete tmp;
        }
    }
};

int main() {
    int n;
    cin >> n;
    vector<Point> pts(n);
    for (auto& p : pts) cin >> p.x >> p.y;

    vector<Line> lines;
    for (int i = 0; i < n; ++i)
        lines.push_back({pts[i].x, -pts[i].y, i});

    set<pair<Point, pair<int, int>>> xEvents;
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
            if (fabs(lines[i].a - lines[j].a) > EPS) {
                Point intersection = getIntersection(lines[i], lines[j]);
                xEvents.insert({intersection, {i, j}});
            }

    vector<Line> sortedLines = lines;
    sort(sortedLines.begin(), sortedLines.end(), [&](const Line& l1, const Line& l2) {
        return l1.getY(-1e9) < l2.getY(-1e9);
    });

    LinkedList status;
    status.build(sortedLines);

    double minArea = DBL_MAX;
    tuple<Point, Point, Point> bestTriangle;

    for (auto& event : xEvents) {
        Point X = event.first;
        int i = event.second.first, j = event.second.second;

        // Swap lines
        status.swapNodes(i, j);

        // Try triangles with neighbors
        for (int lineId : {i, j}) {
            auto [aboveId, belowId] = status.getAdjacent(lineId);
            for (int otherId : {aboveId, belowId}) {
                if (otherId == -1) continue;
                if (!isDistinct(i, j, otherId)) continue;

                Point p1 = pts[i];
                Point p2 = pts[j];
                Point p3 = pts[otherId];
                double area = triangleArea(p1, p2, p3);
                if (area > 1e-6 && area < minArea) {
                    minArea = area;
                    bestTriangle = {p1, p2, p3};
                }
            }
        }
    }

    auto [p1, p2, p3] = bestTriangle;
    cout << fixed << setprecision(10);
    cout << p1.x << " " << p1.y << "\n";
    cout << p2.x << " " << p2.y << "\n";
    cout << p3.x << " " << p3.y << "\n";

    return 0;
}
