import pytest
from abnormal_hieratic_indexer.index_annotations import Indexer

def test_create_indexer():
    with pytest.raises(TypeError):
        indexer = Indexer()
