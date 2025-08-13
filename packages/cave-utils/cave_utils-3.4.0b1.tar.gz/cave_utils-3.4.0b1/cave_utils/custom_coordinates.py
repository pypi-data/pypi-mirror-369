import math
import type_enforced

class CustomCoordinateSystem():
    @type_enforced.Enforcer
    def __init__(self, length: float | int, width: float | int, height: float | int = 10000):
        """
        Creates a custom 2D or 3D Cartesian coordinate system with the origin (0, 0) located at the bottom-left
        of the map and x and y increasing in value whilst moving right and up along the flat plane, respectively. z
        increases whilst moving up along the vertical axis.

        Arguments:

        * **`length`**: `[float | int]` &rarr; The maximum x value of this coordinate system. Must be greater than 0.
        * **`width`**: `[float | int]` &rarr; The maximum y value of this coordinate system. Must be greater than 0.
        * **`height`**: `[float | int]` = `10000` &rarr; The maximum z value of this coordinate system. Must be greater than 0.

        Returns:

        * `[None]`
        """
        self.length = length
        self.width = width
        self.height = height
        self.radius = max(length, width) / (2 * math.pi)
        self.margin = abs(length - width) / 2
        self.__validate_coordinate_system__()

    def serialize_coordinates(self, coordinates: list[list[float | int]]):
        """
        Serializes (x, y, z) coordinates in this coordinate system to a longitude-latitude-altitude system.
        Formula adapted from: https://en.wikipedia.org/wiki/Mercator_projection#Derivation

        Arguments:

        * **`coordinates`**: `list[list[float | int]]` &rarr; The coordinates to be converted in this coordinate system in the format `[[x1,y1,(optional z1)],[x2,y2,(optional z2)],...]`.
            * ** Example **: `[[0,0],[103.5,99.1],[76.55,350],[12.01,12.01]]`
            * ** Example with Altitude **: `[[0,0,0],[103.5,99.1,1],[76.55,350,0.2],[12.01,12.01,3.41]]`
            * ** Note **: All coordinates must have either no altitude or altitude values. There cannot be a mix of both.

        Returns:

        * `[list[list[float | int]]]` &rarr; The converted coordinates in the format `[[long1,lat1,(possible alt1)],[long2,lat2,(possible alt2)],...]` .
        """
        self.__validate_list_coordinates__(coordinates)
        long_lat_coordinates = []
        has_altitude = len(coordinates[0]) == 3
        if has_altitude:
            scale = 10000 / self.height

        for coordinate in coordinates:
            x = coordinate[0]
            y = coordinate[1] - self.width / 2
            if has_altitude: 
                z = coordinate[2]
                altitude = z * scale

            if self.width > self.length:
                x += self.margin

            longitude = (x / self.radius) * (180 / math.pi)
            latitude = (360 / math.pi) * (math.atan(math.exp(y / self.radius)) - math.pi / 4)

            # Y values close to 0 will not display on map 
            if latitude < -85.05 and coordinate[1] >= 0:
                latitude = -85.05
            long_lat_coordinates.append([longitude - 180, latitude, altitude] if has_altitude else [longitude - 180, latitude])

        return long_lat_coordinates

    def serialize_nodes(self, coordinates: list[list[float | int]] | dict[str, list[float | int]]):
        """
        Serialize the given node coordinates in this coordinate system to a dictionary of the proper format.

        Arguments:

        * **`coordinates`**: `[list[list[float | int]] | dict[str, list[float | int]]]` &rarr; The coordinates to be serialized in this coordinate system in the format `[[x1,y1],[x2,y2],...]` or a dictionary with "x", "y", and an optional "z" key with lists of values for all coordinates.
            * ** Example List Type **: `[[0,0],[103.5,99.1],[76.55,350],[12.01,12.01]]`
            * ** Example Dictionary Type with Altitude **: `{"x": [0,103.5,76.55,12.01], "y": [0,99.1,350,12.01], "z": [0,1,0.2,3.41]}`

        Returns:

        * `[dict]` &rarr; The serialized location structure.
        """
        if isinstance(coordinates, list):
            converted_coordinates = self.serialize_coordinates(coordinates)
        elif isinstance(coordinates, dict):
            self.__validate_dict_coordinates__(coordinates)
            if "z" in coordinates:
                list_coordinates = [list(coordinate_list) for coordinate_list in zip(coordinates["x"], coordinates["y"], coordinates["z"])]
            else:
                list_coordinates = [list(coordinate_list) for coordinate_list in zip(coordinates["x"], coordinates["y"])]
            converted_coordinates = self.serialize_coordinates(list_coordinates)
        else:
            raise ValueError("Coordiates must be a list of coordinate values or a dictionary with 'x', 'y', and optional 'z' keys.")

        if len(converted_coordinates[0]) == 2:
            return {
                "latitude": [[coordinate[1]] for coordinate in converted_coordinates],
                "longitude": [[coordinate[0]] for coordinate in converted_coordinates],
                }
        return {
            "latitude": [[coordinate[1]] for coordinate in converted_coordinates],
            "longitude": [[coordinate[0]] for coordinate in converted_coordinates],
            "altitude": [[coordinate[2]] for coordinate in converted_coordinates],
            }
    
    def serialize_arcs(self, path: list[list[list[float | int]]] | list[dict[str, list[float | int]]]):
        """
        Serializes the given path in this coordinate system to a dictionary of the proper format.

        Arguments:

        * **`path`**: `[list[list[list[float | int]]] | list[dict[str, list[float | int]]]]` &rarr; The path coordinates to be serialized in this coordinate system in the format `[[[x1,y1],[x2,y2]],...]` or a list of dictionaries with "x", "y", and an optional "z" key with lists of values for all coordinates of an arc.
            * ** Example List Type **: `[[[0,0],[103.5,99.1]],[[76.55,350],[12.01,12.01]]]`
            * ** Example Dictionary Type with Altitude **: `[{"x": [0,103.5], "y": [0,99.1], "z": [0,1]}, {"x": [76.55,12.01], "y": [350,12.01], "z": [0.2,3.41]}]`

        Returns:

        * `[dict]` &rarr; The serialized location structure.    
        """
        # Additional validation for paths
        if isinstance(path[0], list):
            flattened_path = [coordinate for arc in path for coordinate in arc]
            self.__validate_list_coordinates__(flattened_path)
        elif isinstance(path[0], dict):
            if not all(len(arc) == len(path[0]) for arc in path):
                raise ValueError("All arcs must have either two or three coordinate values.")
        else:
            raise ValueError("Path must be a list of arcs, where each arc is either a list of coordinates or a dictionary with 'x', 'y', and optional 'z' keys.")

        converted_path = []
        for arc in path:
            if isinstance(arc, list):
                converted_arc = self.serialize_coordinates(arc)
            elif isinstance(arc, dict):
                self.__validate_dict_coordinates__(arc)
                if "z" in arc:
                    list_coordinates = [list(coordinate_list) for coordinate_list in zip(arc["x"], arc["y"], arc["z"])]
                else:
                    list_coordinates = [list(coordinate_list) for coordinate_list in zip(arc["x"], arc["y"])]
                converted_arc = self.serialize_coordinates(list_coordinates)
            else:
                raise ValueError("Arc must be a list of coordinates or a dictionary with 'x', 'y', and optional 'z' keys.")
            converted_path.append(converted_arc)
        return {
            "path": converted_path,
        }
    
    def __validate_coordinate_system__(self):
        """
        Validates that the coordinate system has been initialized with valid dimensions (>0).

        Raises:

        * **`ValueError`** &rarr; If the coordinate system dimensions are invalid.
        """
        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("Length, width, and height must be positive.")

    def __validate_list_coordinates__(self, coordinates: list[list[float | int]]):
        """
        Validates that the given coordinates are in the proper format.

        Arguments:

        * **`coordinates`**: `list[list[float | int]]` &rarr; The coordinates to be validated.

        Raises:

        * **`ValueError`** &rarr; If the coordinate data is not in the proper format.
        """
        if not (all(len(coord) == 2 for coord in coordinates) or all(len(coord) == 3 for coord in coordinates)):
            raise ValueError("Coordinates must all have either two elements or three elements.")
        for coordinate in coordinates:
            if not (0 <= coordinate[0] <= self.length and 0 <= coordinate[1] <= self.width):
                raise ValueError("The given x and y coordinates are out of range.")
            if len(coordinate) == 3 and not (0 <= coordinate[2] <= self.height):
                raise ValueError("The given z coordinates are out of range.")

    def __validate_dict_coordinates__(self, coordinates: dict[str, list[float | int]]):
        """
        Validates that the given coordinates are in the proper format.

        Arguments:

        * **`coordinates`**: `dict[str, list[float | int]]` &rarr; The coordinates to be validated.

        Raises:

        * **`ValueError`** &rarr; If the coordinate data is not in the proper format.
        """
        if "x" not in coordinates or "y" not in coordinates:
            raise ValueError("Coordinates must contain 'x' and 'y' keys.")
        if len(coordinates["x"]) != len(coordinates["y"]):
            raise ValueError("The number of x and y values must match.")
        if not (all(0 <= x <= self.length for x in coordinates["x"]) and all(0 <= y <= self.width for y in coordinates["y"])):
            raise ValueError("The given x and y coordinates are out of range.")
        if "z" in coordinates:
            if len(coordinates["x"]) != len(coordinates["z"]):
                raise ValueError("The number of z values must match x and y.")
            if not all(0 <= z <= self.height for z in coordinates["z"]):
                raise ValueError("The given z coordinates are out of range.")
