# Road graph data pipeline

The default bounding box covers Connaught Place in New Delhi. Pass west, south, east,
north to the acquisition CLI to select another area. OSMnx 2.0.3 requests the drive
network, simplifies intersections, retains every component and clips to the box.
Downloads occur only on explicit request. OpenStreetMap data is attributed to
OpenStreetMap contributors and reflects the upstream snapshot at acquisition time.

Each directed MultiDiGraph edge retains its endpoints, key, one-way tags, geometry
and OSM attributes. Length comes from OSMnx in metres. The minimum interpretable
positive maxspeed value supplies a speed estimate. Bare numbers use km/h and mph
uses a factor of 1.609344. Fallback speeds in km/h are motorway 80, trunk 60,
primary 50, secondary 40, tertiary 35, residential 25, living_street 10,
service 15, and unclassified or unknown 25. Multiple classes use the lowest
fallback. Each edge records its speed source. Estimated seconds equal metres
times 3.6 divided by km/h. These are static estimates.

Validation checks CRS, coordinates, finite weights, derived times, graph type,
dataset identity and counts. Disconnected components and isolates are warnings.
Adjacency entries preserve each outgoing keyed edge, including empty lists at
sinks. Matrices use explicit node order, minimum parallel cost, infinity for
missing links and zero diagonal. The default limit is 100 nodes.

GraphML stores integer node IDs and edge keys. JSON attribute payloads retain OSM
lists and booleans. Geometry uses WKT. A metadata copy accompanies the GraphML
and a matching JSON sidecar identifies each dataset. Each file is replaced
atomically. The reader rejects mismatched pairs. Saving verifies the round trip
before publication. Cache IDs hash normalized acquisition parameters. A valid
cache precedes download unless refresh is requested. Acquisition errors fall
back to a verified cache or the bundled synthetic graph and retain a notice.

Density is directed edge count divided by n(n−1), including multiplicity.
Lengths count each direction separately. Parallel pairs count ordered endpoint
pairs with multiple keys. Degree extrema use total degree. Display samples the
first 500 nodes and edges in storage order. Offline tiles depend on browser
availability. Inspection and statistics use local files.

Generate the 16-node synthetic grid using the README command. Its topology and
weights are deterministic. Creation times reflect generation time. A future OSM
download can differ as contributors edit roads. Retain a dataset pair to
reproduce experiments.
