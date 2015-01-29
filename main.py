import sys
import pdb
import svgfig
import json
import math

argv = {}
argv["json"] = 0
argv["max-time"] = 0
argv["max-nodes"] = 0
g = svgfig.SVG("g")
nodes = set()
offset = 15
groups = {}

# BEGIN FUNCTIONS
def ask_args():
	sys.stderr.write(" Input number of nodes[" + str(argv["max-nodes"]) + "]:\n")
	user_maxnodes = raw_input()
	if user_maxnodes != '':
		argv["max-nodes"] = int(user_maxnodes)
	sys.stderr.write(" Input maximum time [" + str(argv["max-time"]) + "]:\n")
	user_maxtime = raw_input()
	if user_maxtime != '':
		argv["max-time"] = int(user_maxtime)

def infer_args():
	if argv["json"] == 0:
		inputfile = open(sys.argv[1])
		for line in inputfile.readlines():
			contents = line.split(" ")
			t = int(contents[0])
			u = int(contents[1])
			v = int(contents[2])

			if t > argv["max-time"]:
				argv["max-time"] = t
			if u > argv["max-nodes"]:
				argv["max-nodes"] = u
			if v > argv["max-nodes"]:
				argv["max-nodes"] = v
		inputfile.close()
	else:
		json_struct = json.loads(open(sys.argv[1], "r").read())
		for link in json_struct:
			argv["max-time"] = max(argv["max-time"], json_struct[link]["time"])
			argv["max-nodes"] = max(argv["max-nodes"], json_struct[link]["from"], json_struct[link]["to"])



def show_help():
	print("Usage: main.py input_file [--json=1] [--output=<out.svg>]")
	print("Input file is either a text file containing t u v, or a JSON file where the following properties are available:")
	print("    from")
	print("    to")
	print("    time")
	print("    color: to be chosen in http://www.december.com/html/spec/colorsvg.html")
	# print("    group: Group ID (any number) offers the opportunity to color groups of links identically")

def read_argv():
	for arg in sys.argv:
		if "=" in arg:
			content = arg.split("=")
			arg_name = content[0].replace("--", "")
			argv[arg_name] = content[1]

def version():
	sys.stderr.write("\tTempNetSVG 1.0 -- Jordan Viard 2015\n")
# END FUNCTIONS

# BEGIN MAIN PROGRAM
if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv :
	show_help()
	sys.exit()
if "-v" in sys.argv or "--version" in sys.argv:
	version()
	exit()

read_argv()

## Infer max-nodes/times from input file, and confirm
infer_args()
ask_args()

sys.stderr.write(" I will now generate a drawing of file " + str(sys.argv[1]) + ", containing " + str(argv["max-nodes"]) + " nodes over " + str(argv["max-time"]) + " instants of time."+ "\n")

# Define dimensions

width = 25 + 10*int(argv["max-time"])
svgfig._canvas_defaults["width"] = str(width) + 'px'

height = 2 + 10*int(argv["max-nodes"])
svgfig._canvas_defaults["height"] = str(height) + 'px'

origleft = 5
origtop = 0

#For groups only
hoffset = 0
voffset = 10
################

# Draw background lines
for i in range(1, int(argv["max-nodes"]) + 1):
	# g.append(svgfig.SVG("text", str(chr(96+i)), x=str(origleft) + "px", y=10*i+origtop, fill="black", stroke_width=0, style="font-size:6"))
	g.append(svgfig.SVG("line", stroke_dasharray="2,2", stroke_width=0.5, x1=str(origleft + 5) + "px", y1=10*i+origtop, x2=width - 5, y2=10*i + origtop))

# Add timearrow
# g.append(svgfig.SVG("line", stroke_width=0.5, x1=10, y1=10+10*int(argv["max-nodes"]) , x2=25+10*int(argv["max-time"]), y2=10+10*int(argv["max-nodes"])))
# g.append(svgfig.SVG("line", stroke_width=0.5, x1=22+10*int(argv["max-time"]), y1=7+10*int(argv["max-nodes"]) , x2=25+10*int(argv["max-time"]), y2=10+10*int(argv["max-nodes"])))
# g.append(svgfig.SVG("line", stroke_width=0.5, x1=22+10*int(argv["max-time"]), y1=13+10*int(argv["max-nodes"]) , x2=25+10*int(argv["max-time"]), y2=10+10*int(argv["max-nodes"])))
# g.append(svgfig.SVG("text", str("Time"), x=25+10*int(argv["max-time"]) , y=-4+10*int(argv["max-time"]) , fill="black", stroke_width=0, style="font-size:4"))
#
# # Add time ticks
# for i in range(0, int(argv["max-time"])):
# 	if i % 5 == 0:
# 		if i == 0:
# 			g.append(svgfig.SVG("line", stroke_width=0.5, x1=10 , y1=10+10*int(argv["max-nodes"]), x2=10 , y2=12+10*int(argv["max-nodes"])))
# 			g.append(svgfig.SVG("text", str(i), x=10 , y=-2+10*int(argv["max-time"]) , fill="black", stroke_width=0, style="font-size:6"))
# 		else:
# 			g.append(svgfig.SVG("line", stroke_width=0.5, x1=offset*i , y1=10+10*int(argv["max-nodes"]), x2=offset*i , y2=12+10*int(argv["max-nodes"])))
# 			g.append(svgfig.SVG("text", str(i), x=offset*i , y=-2+10*int(argv["max-time"]) , fill="black", stroke_width=0, style="font-size:6"))

# Transform file of triplets into JSON structure, or load JSON structure
links_to_json = []
# If we are reading from a JSON file
if int(argv["json"]) is 1:
	json_struct = json.loads(open(sys.argv[1], "r").read())
	for link in json_struct:
		new_link = {}
		new_link["time"] = int(json_struct[link]["time"])
		new_link["from"] = min(int(json_struct[link]["from"]), int(json_struct[link]["to"]))
		new_link["to"] = max(int(json_struct[link]["from"]), int(json_struct[link]["to"]))
		if json_struct[link].get("color") is not None:
			new_link["color"] = json_struct[link]["color"]
		else:
			new_link["color"] = "black"

		if json_struct[link].get("curved") is not None:
			new_link["curved"] = json_struct[link]["curved"]
		else:
			new_link["curved"] = 1

		if json_struct[link].get("group") is not None:
			new_link["group"] = json_struct[link]["group"]
			groupID = json_struct[link]["group"]
			groups[groupID] = {}
			groups[groupID]["timeStart"] = 100000
			groups[groupID]["timeEnd"] = 0
			groups[groupID]["nodeStart"] = 100000
			groups[groupID]["nodeEnd"] = 0
		else:
			new_link["group"] = None

		links_to_json.append(new_link)
# Otherwise, we have to transform the file into a dict structure
else:
	with open(sys.argv[1], 'r') as infile:
		for line in infile:
			link = {}
			contents = line.split(" ")
			link["time"] = int(contents[0])
			link["from"] = min(int(contents[1].strip()),int(contents[2].strip()))
			link["to"] = max(int(contents[1].strip()),int(contents[2].strip()))
			link["color"] = "black"
			link["curved"] = 1
			link["group"] = None
			links_to_json.append(link)

# Read JSON structure
for link in links_to_json:
	ts = link["time"]
	node_1 = link["from"]
	node_2 = link["to"]
	offset = ts*10 + 15

	# Add nodes
	g.append(g.append(svgfig.SVG("circle", cx=origleft + offset, cy=10*node_1, r=1, fill=link["color"])))
	g.append(g.append(svgfig.SVG("circle", cx=origleft + offset, cy=10*node_2, r=1, fill=link["color"])))

	# Draw path between nodes according to specified curving -- links can be curved or not.
	if link["curved"] is 1:
		x = 0.2*((10*node_2 - 10*node_1)/math.tan(math.pi/3)) + origleft + offset
		y = (10*node_1 + 10*node_2) / 2

		g.append(svgfig.SVG("path", stroke=link["color"],d="M" + str(origleft + offset) + "," + str(10*node_1) + " C" + str(x) + "," + str(y) + " " + str(x) + "," + str(y) + " " + str(origleft + offset) + "," + str(10*node_2)))
	else:
		g.append(svgfig.SVG("line", x1=offset, y1=10*node_1, x2=offset, y2=10*node_2, stroke=link["color"]))

	if link["group"] is not None:
		groupID = int(link["group"])
		if groups[groupID]["timeStart"] > link["time"]:
			groups[groupID]["timeStart"] = link["time"]

		if groups[groupID]["timeEnd"] < link["time"]:
			groups[groupID]["timeEnd"] = link["time"]

		if groups[groupID]["nodeStart"] > min(link["from"], link["to"]):
			groups[groupID]["nodeStart"] = min(link["from"], link["to"])

		if groups[groupID]["nodeEnd"] < max(link["from"], link["to"]):
			groups[groupID]["nodeEnd"] = max(link["from"], link["to"])

# Draw groups
# for group in groups:
# 	print "Time start : " + str(groups[group]["timeStart"]*hoffset)
# 	print "Time end : " + str(groups[group]["timeEnd"]*hoffset)
# 	print "Node start : " + str(groups[group]["nodeStart"])
# 	print "Node end : " + str(groups[group]["nodeEnd"])

	# g.append(svgfig.SVG("rect", x=str(groups[group]["timeStart"]*hoffset), y=str(groups[group]["nodeStart"]*voffset), width=str(groups[group]["timeEnd"]*hoffset - groups[group]["timeStart"]*hoffset - 21), height=str(groups[group]["nodeEnd"]*voffset - groups[group]["nodeStart"]*voffset), style="fill:blue;stroke:blue;stroke-width:1;fill-opacity:0;stroke-opacity:0.9"))

# Save to svg file
if argv.get("output") is not None:
	svgfig.canvas(g, viewBox="0 0 " + str(width) + " " + str(height)).save(argv["output"])
	sys.stderr.write("Output generated to "+ str(argv["output"]) + ".\n")
else:
	svgfig.canvas(g, viewBox="0 0 " + str(width) + " " + str(height)).save("out.svg")
	sys.stderr.write(" Output generated to out.svg.\n")
