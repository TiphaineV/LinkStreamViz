import sys
import pdb
import svgfig
import json

argv = {}
g = svgfig.SVG("g")
nodes = set()
offset = 15

# BEGIN FUNCTIONS
def show_help():
	print("Usage: draw_link_streams.py input_file --max_nodes=<N> --max-time=<T> [--output=<out.svg>]")
	print("Input file is either a text file containing t u v, or a JSON file where the following properties are available:")
	print("    from")
	print("    to")
	print("    time")
	print("    curved:[-1|0|1]")
	print("    color: to be chosen in [red|blue|green]")
	print("    group: Group ID (any number) offers the opportunity to color groups of links identically")

def read_argv():
	for arg in sys.argv:
		if "=" in arg: 
			content = arg.split("=")
			arg_name = content[0].replace("--", "")
			argv[arg_name] = content[1]
# END FUNCTIONS

# BEGIN MAIN PROGRAM
if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv :
	show_help()
	sys.exit()

read_argv()

# Draw background lines
for i in range(1, int(argv["max-nodes"]) + 1):
	g.append(svgfig.SVG("text", str(i), x=5, y=10*i+3, fill="black", style="font-size:8"))
	g.append(svgfig.SVG("line", x1=10, y1=10*i, x2=15+10*int(argv["max-time"]), y2=10*i))
	
# Transform file of triplets into JSON structure, or load JSON structure


# Read JSON structure
with open(sys.argv[1], 'r') as infile:
	for line in infile:
		contents = line.split(" ")
		ts = int(contents[0])
		node_1 = int(contents[1].strip())
		node_2 = int(contents[2].strip())
		offset = ts*10 + 15

		g.append(g.append(svgfig.SVG("circle", cx=offset, cy=10*node_1, r=1, fill="black")))
		g.append(g.append(svgfig.SVG("circle", cx=offset, cy=10*node_2, r=1, fill="black")))
		
		if node_1 == node_2+1 or node_2 == node_1 +1:
			g.append(svgfig.SVG("line", x1=offset, y1=10*node_1, x2=offset, y2=10*node_2))
		else:
			g.append(svgfig.SVG("path", d="M" + str(offset) + "," + str(10*node_1) + " C" + str(offset+5) + "," + str(((10*node_1 + 10*node_2)/2)) + " " + str(offset+5) + "," + str(((10*node_1 + 10*node_2)/2)) + " " + str(offset) + "," + str(10*node_2)))
		# g.append(svgfig.SVG("path", d="M" + str(offset) + "," + str(10*node_1) + " C10,10 25,10 25,20"))
# Save to svg file
if argv.get("output") is not None:
	g.save(argv["output"])
else: 
	g.save("out.svg")

