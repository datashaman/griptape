import pytest

from griptape.artifacts import AudioArtifact
from griptape.loaders import AudioLoader


class TestAudioLoader:
    @pytest.fixture
    def loader(self):
        return AudioLoader()

    @pytest.fixture
    def create_source(self, bytes_from_resource_path):
        return bytes_from_resource_path

    @pytest.mark.parametrize("resource_path,suffix,mime_type", [("sentences.wav", ".wav", "audio/wav")])
    def test_load(self, resource_path, suffix, mime_type, loader, create_source):
        source = create_source(resource_path)

        artifact = loader.load(source)

        assert isinstance(artifact, AudioArtifact)
        assert artifact.name.endswith(suffix)
        assert artifact.mime_type == mime_type
        assert len(artifact.value) > 0

    def test_load_collection(self, create_source, loader):
        resource_paths = ["sentences.wav", "sentences2.wav"]
        sources = [create_source(resource_path) for resource_path in resource_paths]

        collection = loader.load_collection(sources)

        assert len(collection) == len(resource_paths)

        keys = {loader.to_key(source) for source in sources}
        for key in collection.keys():
            artifact = collection[key]
            assert isinstance(artifact, AudioArtifact)
            assert artifact.name.endswith(".wav")
            assert artifact.mime_type == "audio/wav"
            assert len(artifact.value) > 0
