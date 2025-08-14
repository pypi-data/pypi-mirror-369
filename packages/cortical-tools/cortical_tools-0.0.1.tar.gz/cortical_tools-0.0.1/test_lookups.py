from cortexclient.datasets.v1dd import client
from cortexclient.mesh_vertex import *

rid = 864691132544823185
vass = VertexAssigner(root_id=rid, caveclient=client.cave)

if __name__ == "__main__":
    vass.compute_mesh_labels(n_jobs=1)
