import heapq
import sys
from collections import namedtuple, defaultdict
from shapely.geometry import LineString, Point as ShapelyPoint
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import warnings
warnings.filterwarnings("ignore")

EPS = 1e-6
Event = namedtuple("Event", ["x","y","type","point","segments"])

def dcmp(x):
    if x < -EPS: return -1
    if x > EPS:  return 1
    return 0

# Check if point p lies on segment seg
def is_interior(seg, p):
    (x1,y1),(x2,y2) = seg.p1, seg.p2
    cross = (y2-y1)*(p[0]-x1) - (x2-x1)*(p[1]-y1)
    if abs(cross)>EPS: return False
    return min(x1,x2)-EPS <= p[0] <= max(x1,x2)+EPS and \
           min(y1,y2)-EPS <= p[1] <= max(y1,y2)+EPS

class Segment:
    def __init__(self,p1,p2,index):
        if p1[0]>p2[0] or (dcmp(p1[0]-p2[0])==0 and p1[1]>p2[1]):
            p1,p2 = p2,p1
        self.p1,self.p2 = p1,p2
        self.index = index
        self.geom = LineString([p1,p2])
    def get_y(self,x):
        t = (x-self.p1[0])/(self.p2[0]-self.p1[0])
        return self.p1[1] + t*(self.p2[1]-self.p1[1])
    def __lt__(self,other):
        y1=self.get_y(SweepLine.x)
        y2=other.get_y(SweepLine.x)
        if dcmp(y1-y2)!=0: return y1<y2
        return self.index<other.index

class Node:
    def __init__(self,seg):
        self.seg = seg
        self.link = [None,None]
        self.par = None
        self.prev = None
        self.next = None

class SplayTree:
    def __init__(self): self.root=None
    def rotate(self,x):
        p=x.par
        if not p: return
        g=p.par
        if p.link[0] is x:
            p.link[0]=x.link[1]
            if x.link[1]: x.link[1].par=p
            x.link[1]=p
        else:
            p.link[1]=x.link[0]
            if x.link[0]: x.link[0].par=p
            x.link[0]=p
        p.par=x
        x.par=g
        if g:
            if g.link[0] is p: g.link[0]=x
            else:           g.link[1]=x
        else:
            self.root=x
    def splay(self,x):
        while x.par:
            p=x.par
            g=p.par
            if not g: self.rotate(x)
            elif (g.link[0] is p)==(p.link[0] is x):
                self.rotate(p); self.rotate(x)
            else:
                self.rotate(x); self.rotate(x)
    def insert(self,node):
        pred=succ=None
        cur=self.root
        while cur:
            if cur.seg<node.seg:
                pred=cur; cur=cur.link[1]
            else:
                cur=cur.link[0]
        cur=self.root
        while cur:
            if node.seg<cur.seg:
                succ=cur; cur=cur.link[0]
            else:
                cur=cur.link[1]
        if not self.root:
            self.root=node; return
        if pred:
            self.splay(pred)
            node.link[1]=pred.link[1]
            if node.link[1]: node.link[1].par=node
            pred.link[1]=node
            node.par=pred
            node.prev=pred; node.next=pred.next
            if pred.next: pred.next.prev=node
            pred.next=node
        else:
            self.splay(succ)
            node.link[0]=succ.link[0]
            if node.link[0]: node.link[0].par=node
            succ.link[0]=node
            node.par=succ
            node.next=succ; node.prev=succ.prev
            if succ.prev: succ.prev.next=node
            succ.prev=node
    def erase(self,node):
        if node.prev: node.prev.next=node.next
        if node.next: node.next.prev=node.prev
        self.splay(node)
        if not node.link[0]:
            self.root=node.link[1]
            if self.root: self.root.par=None
        else:
            L=node.link[0]; L.par=None
            m=L
            while m.link[1]: m=m.link[1]
            self.splay(m)
            m.link[1]=node.link[1]
            if m.link[1]: m.link[1].par=m
            self.root=m
        node.link=[None,None]; node.par=None; node.prev=node.next=None

class SweepLine:
    x=-1e20
    def __init__(self):
        self.tree=SplayTree()
        self.events=[]
        self.intersections=set()
        self.node_map={}
        self.point_to_segments=defaultdict(set)

    def add_segment(self,seg):
        heapq.heappush(self.events,Event(seg.p1[0],seg.p1[1],'start',seg.p1,[seg]))
        heapq.heappush(self.events,Event(seg.p2[0],seg.p2[1],'end',seg.p2,[seg]))

    def add_intersection_event(self,p,s1,s2):
        heapq.heappush(self.events,Event(p.x,p.y,'intersect',(p.x,p.y),[s1,s2]))

    def handle_event(self,p,segs):
        U=[s for s in segs if s.p1==p]
        L=[s for s in segs if s.p2==p]
        C=[s for s in segs if s not in U and s not in L and is_interior(s,p)]
        if len(U)+len(L)+len(C)>=2:
            pt=(round(p[0],3),round(p[1],3))
            self.intersections.add(pt)
            self.point_to_segments[pt].update([s.index for s in U+L+C])
        for s in L+C:
            node=self.node_map.pop(s,None)
            if node: self.tree.erase(node)
        C.reverse()
        for s in U+C:
            node=Node(s)
            self.node_map[s]=node
            self.tree.insert(node)
        combo=U+C
        if not combo:
            sl=node.prev.seg if node.prev else None
            sr=node.next.seg if node.next else None
            self.check_intersection(sl,sr)
        else:
            s0=min(combo,key=lambda s:(s.get_y(SweepLine.x),s.index))
            s00=max(combo,key=lambda s:(s.get_y(SweepLine.x),s.index))
            n0=self.node_map[s0]; n1=self.node_map[s00]
            cur = n0.prev
            while cur:
                # Check if they intersect at the current sweep line x (optional but helps terminate early)
                if not self.check_intersection(cur.seg, s0):  # You can use a custom function or bounding box overlap
                    break
                cur = cur.prev

            # Traverse downwards to check intersections
            cur = n1.next
            while cur:
                # Check if they intersect at the current sweep line x (optional but helps terminate early)
                if not self.check_intersection(cur.seg, s00):  # You can use a custom function or bounding box overlap
                    break
                cur = cur.next
    def check_intersection(self,s1,s2):
        if not s1 or not s2 or s1.index==s2.index: return
        # print(f"Checking intersection between {s1.index} and {s2.index}")
        inter=s1.geom.intersection(s2.geom)
        if inter.is_empty: return
        pts=[inter] if inter.geom_type=='Point' else (inter.geoms if hasattr(inter,'geoms') else [])
        for p in pts:
            pt=(round(p.x,3),round(p.y,3))
            if pt not in self.intersections:
                self.intersections.add(pt)
                self.add_intersection_event(p,s1,s2)
            self.point_to_segments[pt].update([s1.index,s2.index])
        if pts==[]:
            return False
        else:
            return True
    def run(self):
        while self.events:
            e=heapq.heappop(self.events)
            SweepLine.x=e.x
            batch=[e]
            while self.events and dcmp(self.events[0].x-e.x)==0:
                batch.append(heapq.heappop(self.events))
            batch.sort(key=lambda ev:(ev.x,{'start':0,'intersect':1,'end':2}[ev.type]))
            for ev in batch:
                SweepLine.x=ev.x+20*EPS
                self.handle_event(ev.point,ev.segments)
        return sorted(self.intersections)


def plot_segments_and_intersections(segments, intersections, segments_file, output_file, points_file):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))  # Slightly wider

    with open(points_file, 'r') as f:
        lines = f.read().strip().split()
        k = int(lines[0])
        pts = [tuple(map(float, lines[i * 2 + 1:i * 2 + 3])) for i in range(k)]

    cmap = cm.get_cmap("tab10", len(segments))

    # Plot input points with colors from the color map
    for i, pt in enumerate(pts):
        color = cmap(i % len(segments))  # Get color from the colormap
        ax1.plot(pt[0], pt[1], 'o', color=color, label=f"{pt}")

    # Add title, grid, legend, and equal aspect ratio
    ax1.set_title("Input points")
    ax1.set_aspect('equal')
    ax1.grid(True)
    ax1.legend()

    # --------- RIGHT PLOT: Segments and Intersections ---------
    all_x, all_y = [], []

    for idx, (p1, p2, segment_idx) in enumerate(segments):
        xs, ys = zip(p1, p2)
        all_x.extend(xs)
        all_y.extend(ys)
        ax2.plot(xs, ys, color=cmap(idx))

    if intersections:
        ix, iy = zip(*intersections)
        all_x.extend(ix)
        all_y.extend(iy)
        ax2.plot(ix, iy, 'ro', label='Intersections')

    # Extend x-axis and y-axis range by a margin
    x_margin = (max(all_x) - min(all_x)) * 0.2  # 20% extra width
    y_margin = (max(all_y) - min(all_y)) * 0.1  # 10% extra height
    ax2.set_xlim(min(all_x) - x_margin, max(all_x) + x_margin)
    ax2.set_ylim(min(all_y) - y_margin, max(all_y) + y_margin)

    ax2.set_title("Segments and Intersections")
    ax2.set_aspect('auto')  # Let it stretch horizontally
    ax2.grid(True)

    for idx, (p1, p2, segment_idx) in enumerate(segments):
        ax2.text(1.02, 0.98 - idx * 0.05, f"Segment {segment_idx}", 
                 transform=ax2.transAxes, fontsize=10, color=cmap(idx),
                 ha='left', va='top')

    ax2.legend()

    # Save the combined plot
    image_filename = f"segments_intersections_{segments_file.split('.')[0]}_{output_file.split('.')[0]}.png"
    plt.tight_layout()
    plt.savefig(image_filename)
    print(f"Plot saved as {image_filename}")

if __name__=='__main__':
    if len(sys.argv)!=4:
        print("Usage: python3 q1.py segs.txt out.txt pts.txt")
        sys.exit(1)
    input_file, output_file, points_file = sys.argv[1], sys.argv[2], sys.argv[3]
    # Read segments
    with open(input_file,'r') as f:
        n=int(f.readline())
        segs=[]
        for i in range(n):
            x1,y1,x2,y2=map(float,f.readline().split())
            if dcmp(x1-x2)!=0:
                segs.append(Segment((x1,y1),(x2,y2),i))
    # Run sweep
    sl=SweepLine()
    for s in segs:
        sl.add_segment(s)
    result=sl.run()
    # Write intersections
    with open(output_file,'w') as f:
        f.write("Unique intersection points:\n")
        for x,y in result:
            f.write(f"({x:.3f}, {y:.3f})\n")

    # Process points file for largest collinear subs
    max_pt=None
    max_segs=set()
    for pt,segs_set in sl.point_to_segments.items():
        # print(segs_set,pt)
        if len(segs_set)>len(max_segs):
            max_pt, max_segs = pt, segs_set
    with open(points_file,'r') as f:
        lines=f.read().strip().split() 
        k=int(lines[0])
        pts=[tuple(map(float,lines[i*2+1:i*2+3])) for i in range(k)]
    if max_pt:
        print("Largest subset of points that lie on a common line ::")
        for idx in sorted(max_segs):
            x,y=pts[idx]
            print(f"{x}, {y}")
    else:
        print("No segment intersections found.")
    
    plot_segments_and_intersections([(s.p1, s.p2, s.index) for s in segs], result, input_file, output_file, points_file)