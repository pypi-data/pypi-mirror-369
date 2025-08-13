import logging
import uuid
from typing import List

from terrascope_api.models.analysis_pb2 import AnalysisAlgorithmNode, AnalysisAlgorithmConfigNode
from terrascope_api.models.analysis_version_pb2 import AnalysisManifest as AnalysisManifestPAPI

fmt = "%(levelname)s %(asctime)s %(filename)s:%(lineno)i %(funcName)s pid:%(process)s: %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=fmt,
    datefmt="%H:%M:%S",
)


class AnalysisManifest:
    """
    Description:
    This will be a builder to build analyses in an easy and controlled way. Specifically this will manage the sequence
    of algorithms needed for a analyses. The object structure will be maintained in way that once the build is complete
    the returned object can be submitted to the analyses end point.

    Example:
        Note - dag1 can be any name you want, but each time you call analysesDAGFactory() that creates a new "instance"
            that instance MUST ONLY be used for 1 DAG. If you want to make another tag call the above on a new variable.

        dag1 = analysesDAGFactory()

        dag1.add_node("algo1", "7bd14fed-a6d7-42f7-b1e3-a9b1043ebb16")
        dag1.add_node("algo2", "aa643c56-9420-4707-a7da-bf01f89e18bd")
        dag1.add_node("algo3", "707d9325-a4e6-4d32-8991-47962e1337e8")

    """

    def __init__(self):
        self.__manifest = AnalysisManifestPAPI()

        # Set Default Manifest Version
        self.__manifest.manifest_version = "0.1.0"

    def metadata(self, description: str, tags: List):
        self.__manifest.metadata.description = description
        self.__manifest.metadata.tags.extend(tags)

    def manifest_version(self, version: str):
        self.__manifest.manifest_version = version

    def add_node(self, name: str, algorithm_version_id: str, children: [] = None):
        """
        Description:
            Add a node to the dag. Note, this is a unique name safe generated as it will add a UUID to the end
            of the name given as a suffix to ensure uniqueness.

        :param name: A unique (relative to this analyses) name for this node
        :param algorithm_version_id: The version id of the algorithm that will be executed at this node.
        :param children: these are children algorithms to run from this node.

                     Node1
               //      ||      \\
            Child1   Child2    ...
               \\      ||      //
                     Node2
                       ||
                       ...
        :return:
        """
        if not children:
            children = []
        for node in self.__manifest.algorithm_nodes:
            assert name != node.name
        self.__manifest.algorithm_nodes.append(AnalysisAlgorithmNode(
            name=name,
            algorithm_version_id=algorithm_version_id,
            children=children
        ))

    def add_node_edge(self, parent_index: int, child_index: int):
        """
        Creates a directed edge between two nodes in the dag
        :param parent_index: The parent node index to draw an edge from
        :param child_index: The child node index to draw an edge to
        :return:
        """
        assert 0 <= parent_index <= len(self.__manifest.algorithm_nodes) - 1
        self.__manifest.algorithm_nodes[parent_index].children.append(
            self.__manifest.algorithm_nodes[child_index].name)

    def add_child_node(self, node_index: int, name: str, algorithm_config_id: str):
        """
        Description
         This will be future implementation. Right now child nodes are edges, use alternative method.
        TODO: This is still WIP. Nailing down specifics on child nodes and conditions for add or not.
        :param node_index:
        :param name:
        :param algorithm_config_id:
        :return:
        """
        assert 0 <= node_index <= len(self.__manifest.algorithm_nodes) - 1
        self.__manifest.algorithm_nodes[node_index]['children'].append((
            AnalysisAlgorithmNode(
                name="{}-{}".format(name, uuid.uuid4()),
                algorithm_version_id=algorithm_config_id
            )
        ))

    def get_name(self, node_index: int):
        """
        Description:

        Gets the node name at a specific index.

        :param node_index:
        :return:
        """
        if 0 <= node_index <= len(self.__manifest.algorithm_nodes):
            return self.__manifest.algorithm_nodes[node_index].name

    def get(self) -> AnalysisManifestPAPI:
        return self.__manifest

    # Helper Methods
    def print(self):
        """
        Description
        Helper method to see your graph structure. Not to be used in production code.

        :return:
        """
        for i in range(len(self.__manifest.algorithm_nodes)):
            logging.info("Node-{}:\n\tname: {}\n\talgorithm_version_id: {}\n\tchildren:"
                         .format(i,
                                 self.__manifest.algorithm_nodes[i].name,
                                 self.__manifest.algorithm_nodes[i].algorithm_version_id))
            if self.__manifest.algorithm_nodes[i].children:
                for edge in self.__manifest.algorithm_nodes[i].children:
                    logging.info("\t\tchild_name: {}".format(edge))
            else:
                logging.info("\t\tEmpty")


class AnalysisConfiguration:
    """
    Description:
    This builder will construct the Analysis dag. Use similar to AnalysisDAGFactory.

    """

    def __init__(self, analysis_version_id: str):
        self.__analysis_version_id = analysis_version_id
        self.__analysis_config_nodes = []

    def add_config_node(self, name: str, algorithm_config_id: str, index: int = None):
        """
        Description:
        This method adds an AnalysisAlgorithmConfigNode which references the EXACT node name used to define a node in
        the analyses that you are referencing. It also assigns the Algorithm Configuration ID to that node meaning
        here are the specific runtime specifications.

        :param index: optional - if specified, the node will be inserted before the provided index.
        :param name: The name of the node in the analyses you wish to set the config for. Exact Match required.
        :param algorithm_config_id: The algorithm configuration ID to assign to that node.
        :return:
        """
        if index is None:
            self.__analysis_config_nodes.append(AnalysisAlgorithmConfigNode(
                name=name,
                algorithm_config_id=algorithm_config_id
            ))
        else:
            if not 0 <= index < len(self.__analysis_config_nodes):
                logging.info("Provided index {} is output of bounds".format(index))
            self.__analysis_config_nodes.insert(index, AnalysisAlgorithmConfigNode(
                name=name,
                algorithm_config_id=algorithm_config_id
            ))

    def get(self) -> List:

        return self.__analysis_config_nodes
