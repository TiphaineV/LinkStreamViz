import sys
import pdb
import svgfig
import json
import os
import math
import random


def show_help():
    print("Usage: main.py input_file [--silent] [--output=<out.svg>]" +
          " [--order=order.txt]")
    print("Input file is either a text file containing t u v," +
          "or a JSON file where the following properties are available:")
    print("    from")
    print("    to")
    print("    time")
    print("    color: to be chosen in " +
          "http://www.december.com/html/spec/colorsvg.html")
    print("The orderFile contains a list of all nodes to display " +
          "in the order of appearance in orderFile.")


def read_argv(argv):
    for arg in sys.argv:
        if "=" in arg:
            content = arg.split("=")
            arg_name = content[0].replace("--", "")
            argv[arg_name] = content[1]
        elif "--" in arg:
            arg_name = arg.replace("--", "")
            argv[arg_name] = True


def version():
    sys.stderr.write("\tLinkStreamViz 1.0 -- Jordan Viard 2015\n")


class idGenerator:
    """generates id"""

    def __init__(self):
        self.lookUp = dict()  # dict[Node] = id
        self.idCount = 0
        self.reverse = dict()  # dict[id] = node

    def impose(self, node, id_):
        self.lookUp[node] = id_
        self.reverse[id_] = node

    def contains(self, element):
        return element in self.lookUp

    def get(self, element):

        if element not in self.lookUp:
            while self.idCount in self.reverse and self.reverse[self.idCount] != element:
                self.idCount += 1
            self.lookUp[element] = self.idCount
            self.reverse[self.idCount] = element
        return self.lookUp[element]

    def size(self):
        return len(self.lookUp)


class Link:

    def __init__(self, t, u, v, color="black", direction=0, duration=0, duration_color="black"):
        self.t = float(t)
        self.u = int(min(u, v))
        self.v = int(max(u, v))
        self.color = color
        self.direction = direction
        self.duration = duration
        self.duration_color = duration_color

    @staticmethod
    def from_dict(link):
        obj = Link(link["time"],
                   link["from"],
                   link["to"])
        obj.color = link.get("color", "black")
        obj.direction = link.get("direction", 0)
        obj.duration = float(link.get("duration", 0))
        obj.duration_color = link.get("duration_color", "black")
        return obj


class LinkStream:

    def __init__(self, inputFile, orderFile=""):
        self.links = []
        self.max_time = 0
        self.nodeID = idGenerator()
        self.max_label_len = 0
        self.g = svgfig.SVG("g")
        self.ppux = 10  # piwel per unit time
        if "json" in inputFile:
            with open(inputFile, 'r') as inFile:
                json_struct = json.loads(inFile.read())
                for link_json in json_struct:
                    link = Link.from_dict(link_json)
                    self.addNode(link.u)
                    self.addNode(link.v)
                    if (link.t + link.duration) > self.max_time:
                        self.max_time = link.t + link.duration
                    self.links.append(link)
        else:
            with open(inputFile, 'r') as inFile:
                for line in inFile:
                    contents = line.split(" ")
                    t = float(contents[0])
                    u = int(contents[1])
                    v = int(contents[2])
                    self.addNode(u)
                    self.addNode(v)
                    if t > self.max_time:
                        self.max_time = t
                    self.links.append(Link(t, u, v))
        if orderFile != "":
            tmp_nodes = set()
            with open(orderFile, 'r') as order:
                for i, n in enumerate(order):
                    node = int(n)
                    tmp_nodes.add(node)
                    if self.nodeID.contains(node):
                        self.nodeID.impose(node, i)
                        self.nodes.append(node)
                    else:
                        print('The node', node, "is not present in the stream")
                        exit()
            for node in self.nodeID.lookUp:
                if node not in tmp_nodes:
                    print('The node', node, "is not present in", orderFile)
                    exit()

    def addNode(self, node):
        self.nodeID.get(node)
        if self.max_label_len < len(str(node)):
            self.max_label_len = len(str(node))

    def evaluateOrder(self, order):
        distance = 0
        for link in self.links:
            distance += abs(order[link.u]-order[link.v])
        return distance

    def findOrder(self):
        cur_solution = self.nodeID.lookUp
        cur_reverse = self.nodeID.reverse
        dist = self.evaluateOrder(cur_solution)
        sys.stderr.write("Order improved from "+str(dist))
        for i in range(0, 10000):
            i = random.randint(0, len(cur_solution) - 1)
            j = random.randint(0, len(cur_solution) - 1)
            cur_reverse[j], cur_reverse[i] = cur_reverse[i], cur_reverse[j]
            cur_solution[cur_reverse[j]] = j
            cur_solution[cur_reverse[i]] = i
            tmp = self.evaluateOrder(cur_solution)
            if tmp >= dist:
                # re swap to go back.
                cur_reverse[j], cur_reverse[i] = cur_reverse[i], cur_reverse[j]
                cur_solution[cur_reverse[j]] = j
                cur_solution[cur_reverse[i]] = i
            else:
                dist = tmp
        self.nodeID.lookUp = cur_solution
        new_order = "new_order.txt"
        with open(new_order, "w") as out:
            for node in self.nodeID.reverse:
                out.write(str(self.nodeID.reverse[node]) + "\n")
        sys.stderr.write(" to "+str(dist)+". Order saved in:"+new_order+"\n")

    def addDuration(self, origin, duration, color, amplitude=1):
        freq = 0.8  # angular frequency
        duration = duration * self.ppux
        self.g.append(svgfig.SVG("line",
                                 stroke=color,
                                 stroke_opacity=0.8,
                                 stroke_width=1.1,
                                 x1=origin["x"],
                                 y1=origin["y"],
                                 x2=origin["x"]+duration,
                                 y2=origin["y"]))

    def draw(self, outputFile):
        self.findOrder()
        offset = 1.5 * self.ppux
        # Define dimensions
        label_margin = 5 * self.max_label_len
        origleft = label_margin + 1 * self.ppux

        right_margin = self.ppux
        width = origleft + self.ppux * math.ceil(self.max_time) + right_margin
        svgfig._canvas_defaults["width"] = str(width) + 'px'

        arrow_of_time_height = 5
        height = 5 + 10 * int(self.nodeID.size() + 1) + arrow_of_time_height
        svgfig._canvas_defaults["height"] = str(height) + 'px'

        origtop = 10
        ################
        # Draw background lines
        for node in self.nodeID.lookUp:
            horizonta_axe = self.ppux * self.nodeID.get(node) + origtop
            self.g.append(svgfig.SVG("text", str(node),
                                     x=str(label_margin),
                                     y=horizonta_axe + 2,
                                     fill="black", stroke_width=0,
                                     text_anchor="end",
                                     font_size="6"))
            self.g.append(svgfig.SVG("line", stroke_dasharray="2,2",
                                     stroke_width=0.5,
                                     x1=str(origleft-5),
                                     y1=horizonta_axe,
                                     x2=width - right_margin,
                                     y2=horizonta_axe))

        # Add timearrow
        self.g.append(svgfig.SVG("line",
                                 stroke_width=0.5,
                                 x1=self.ppux ,
                                 y1=10*(self.nodeID.size()+1),
                                 x2=width-5,
                                 y2=10*(self.nodeID.size()+1)))
        self.g.append(svgfig.SVG("line", stroke_width=0.5,
                                 x1=width-8,
                                 y1=10*(self.nodeID.size()+1)-3,
                                 x2=width-5,
                                 y2=10*(self.nodeID.size()+1)))
        self.g.append(svgfig.SVG("line", stroke_width=0.5,
                                 x1=width-8,
                                 y1=10*(self.nodeID.size()+1)+3,
                                 x2=width-5,
                                 y2=10*(self.nodeID.size()+1)))
        self.g.append(svgfig.SVG("text", str("Time"),
                                 x=width-19,
                                 y=10*(self.nodeID.size()+1)-3,
                                 fill="black", stroke_width=0,
                                 font_size="6"))
    #
    # Add time ticks
        for i in range(0, int(math.ceil(self.max_time)+1), 5):
            x_tick = i * self.ppux  + origleft
            self.g.append(svgfig.SVG("line",
                                     stroke_width=0.5,
                                     x1=str(x_tick),
                                     y1=10*(self.nodeID.size()+1)-3,
                                     x2=str(x_tick),
                                     y2=10*(self.nodeID.size()+1)+3))
            self.g.append(svgfig.SVG("text", str(i),
                                     x=str(x_tick), y=10*(self.nodeID.size()+1)+7,
                                     fill="black", stroke_width=0,
                                     font_size="6"))

        for link in self.links:
            ts = link.t
            node_1 = min(self.nodeID.get(link.u), self.nodeID.get(link.v))
            node_2 = max(self.nodeID.get(link.u), self.nodeID.get(link.v))
            offset = ts * self.ppux + origleft
            y_node1 = 10 * node_1 + origtop
            y_node2 = 10 * node_2 + origtop
            # Add nodes
            self.g.append(svgfig.SVG("circle",
                                     cx=offset, cy=y_node1,
                                     r=1, fill=link.color))
            self.g.append(svgfig.SVG("circle",
                                     cx=offset, cy=y_node2,
                                     r=1, fill=link.color))

            x = 0.2 * ((10 * node_2 - 10 * node_1) / math.tan(math.pi / 3)) + offset
            y = (y_node1 + y_node2) / 2

            param_d = "M" + str(offset) + "," + str(y_node1) +\
                      " C" + str(x) + "," + str(y) + " " + str(x) + "," + str(y) +\
                      " " + str(offset) + "," + str(y_node2)
            self.g.append(svgfig.SVG("path", stroke=link.color,
                                     d=param_d))
            self.addDuration({"x": x, "y": (y_node1+y_node2)/2}, link.duration, link.duration_color)
    # Save to svg file
        viewBoxparam = "0 0 " + str(width) + " " + str(height)
        svgfig.canvas(self.g, viewBox=viewBoxparam).save(outputFile)


if __name__ == '__main__':
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit()
    if "-v" in sys.argv or "--version" in sys.argv:
        version()
        exit()

    argv = {"order": "", "silent": False}
    read_argv(argv)
    Links = LinkStream(sys.argv[1], argv["order"])
    default_output = os.path.basename(sys.argv[1]).split(".")[0]+".svg"
    argv["output"] = argv.get("output", default_output)
    Links.draw(argv["output"])
    if not argv["silent"]:
        sys.stderr.write("Output generated to " + argv["output"] + ".\n")
