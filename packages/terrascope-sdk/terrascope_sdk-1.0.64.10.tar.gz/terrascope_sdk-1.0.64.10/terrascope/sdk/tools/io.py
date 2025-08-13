import codecs
import logging
from pathlib import Path

import chardet
import geojson
import h3


class H3Tools:

    def points_to_h3_geometry(self, filename, resolution: int, output: str = None, encoding: str = None):
        """
        This method takes a geojson file, a H3 resolution, and an optional file encoding type. The geojson file
        should be a Point geometry types. This will walk all points in the file, determine the H3 cell at the
        specified resolution value and return the H3 Cell geometry (polygon).

        The final result is a copy of the original file, and the Point geometry type will be replaced with "Polygon"
        geometry.

        Note: When using with TerraScope, write the file out as UTF-8 for compatibility.

        If encoding is not provided, the chardet library will be used to determine the encoding type. If the confidence
        is below 0.60, program will fail. In this case, the user must specify the encoding type. Console will provide
        the estimated encoding type, and what confidence it was determined at if the program asserts due to confidence
        threshold not being met.

        H3 Resolution Table: https://h3geo.org/docs/core-library/restable/#cell-counts
        COUNTS
        Res	Total number of cells	Number of hexagons	Number of pentagons
        0	122	                    110	                12
        1	842	                    830	                12
        2	5,882	                5,870	            12
        3	41,162	                41,150	            12
        4	288,122	                288,110	            12
        5	2,016,842	            2,016,830	        12
        6	14,117,882	            14,117,870	        12
        7	98,825,162	            98,825,150	        12
        8	691,776,122	            691,776,110	        12
        9	4,842,432,842	        4,842,432,830	    12
        10	33,897,029,882	        33,897,029,870	    12
        11	237,279,209,162	        237,279,209,150	    12
        12	1,660,954,464,122	    1,660,954,464,110	12
        13	11,626,681,248,842	    11,626,681,248,830	12
        14	81,386,768,741,882	    81,386,768,741,870	12
        15	569,707,381,193,162	    569,707,381,193,150	12

        SIZE in km^2
        Res	Average Hexagon Area (km2)	Pentagon Area* (km2)	Ratio (P/H)
        0	4,357,449.416078381	        2,562,182.162955496	    0.5880
        1	609,788.441794133	        328,434.586246469	    0.5386
        2	86,801.780398997	        44,930.898497879	    0.5176
        3	12,393.434655088	        6,315.472267516	        0.5096
        4	1,770.347654491	            896.582383141	        0.5064
        5	252.903858182	            127.785583023	        0.5053
        6	36.129062164	            18.238749548	        0.5048
        7	5.161293360	                2.604669397	            0.5047
        8	0.737327598	                0.372048038	            0.5046
        9	0.105332513	                0.053147195	            0.5046
        10	0.015047502	                0.007592318	            0.5046
        11	0.002149643	                0.001084609	            0.5046
        12	0.000307092	                0.000154944	            0.5046
        13	0.000043870	                0.000022135	            0.5046
        14	0.000006267	                0.000003162	            0.5046
        15	0.000000895	                0.000000452	            0.5046

        :param filename: str. The filepath of the .geojson file.
        :param resolution: int. A integer ranging between 0 and 15 inclusive.
        :param encoding: [Optional] str. The encoding type of the file.
        :param output: str. The filepath + filename of the file to be writen
        :return:
        """

        # Ensure resolution is within H3 resolution range.
        assert 0 <= resolution <= 15
        extension = filename.split(".")[-1]
        assert extension == "geojson"
        if encoding is None:
            encoding, confidence = self.determine_encoding(filename)
            logging.info("\nFile: {}\nEncoding: {}\n Confidence: {}".format(filename, encoding, confidence))
            assert confidence >= 0.60

        with codecs.open(filename, encoding=encoding) as f:
            file_content = geojson.load(f)

        for feature in file_content.features:
            # set memory pointer to update list in place
            point = feature.geometry.coordinates
            h3_geom = self.point_to_h3_geometry(lat=point[1], lon=point[0], resolution=resolution)
            polygon = []
            for point in h3_geom:
                polygon.append([point[0], point[1]])

            feature.geometry.type = "Polygon"
            feature.geometry.coordinates = [polygon]

        if output is not None:
            output_ext = output.split(".")[-1]
            assert output_ext == "geojson"
            with codecs.open(output, 'w', encoding="utf-8") as f:
                geojson.dump(file_content, f)

        return file_content

    @staticmethod
    def point_to_h3_geometry(lat, lon, resolution: int) -> str:
        cell_hash = h3.geo_to_h3(lat=lat, lng=lon, resolution=resolution)
        return h3.h3_to_geo_boundary(cell_hash, geo_json=True)

    @staticmethod
    def determine_encoding(filename):
        """
        Detect file encoding

        :param filename: the file to detect the encoding of.
        :return: encoding, and confidence level.

        """
        filepath = Path(filename)

        # We must read as binary (bytes) because we don't yet know encoding
        blob = filepath.read_bytes()

        encoding_detection = chardet.detect(blob)
        encoding = encoding_detection["encoding"]
        confidence = encoding_detection["confidence"]

        return encoding, confidence
