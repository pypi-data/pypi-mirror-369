from scgraph.geographs.marnet import marnet_geograph

from cave_utils import GeoUtils

try:
    count = 10
    out = GeoUtils.create_shortest_paths_geojson(
        geoGraph=marnet_geograph,
        ids=[str(i) for i in range(count)],
        origin_latitudes=[0 + i / 4 for i in range(count)],
        origin_longitudes=[0 + i / 4 for i in range(count)],
        destination_latitudes=[0 - i / 4 for i in range(count)],
        destination_longitudes=[0 - i / 4 for i in range(count)],
        show_progress=False,
        # filename="test.geojson"
    )
    print("GeoUtils Tests: Passed!")
except Exception as e:
    print("GeoUtils Tests: Failed!")
    print(f"Error: {e}")
    raise e
