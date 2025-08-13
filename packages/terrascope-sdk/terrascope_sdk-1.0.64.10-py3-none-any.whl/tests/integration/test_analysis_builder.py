import uuid

from terrascope.sdk.builder.analysis import AnalysisManifest


class TestAnalysisManifest:
    def test_manifest(self):
        manifest = AnalysisManifest()
        manifest_version = "0.0.1"
        description = "Test description for the greatest manifest in the world."
        version = "0.1.0"
        manifest.metadata(description=description,
                          version=version,
                          tags=["sdk-test", "cap-sdk"])
        manifest.add_node(name="fake_name_1",
                          algorithm_version_id=str(uuid.uuid4()))
        manifest.add_node(name="fake_name_child_2",
                          algorithm_version_id=str(uuid.uuid4()))
        manifest.add_node(name="fake_name_child_3",
                          algorithm_version_id=str(uuid.uuid4()))

        manifest.add_node_edge(0, 1)
        manifest.add_node_edge(1, 2)

        manifest_struct = manifest.get()
        assert manifest_struct.metadata.description == description
        assert manifest_struct.metadata.version == version
        assert len(manifest_struct.algorithm_nodes) == 3
