import pytest
from model2vec import StaticModel


@pytest.fixture
def model() -> StaticModel:
    """Load a model for testing."""
    return StaticModel.from_pretrained("tests/data/test_model")


@pytest.fixture(params=[True, False], ids=["use_ann=True", "use_ann=False"])
def use_ann(request: pytest.FixtureRequest) -> bool:
    """Whether to use approximate nearest neighbors or not."""
    return request.param


@pytest.fixture
def train_texts() -> list[str]:
    """A list of train texts for testing outlier and representative filtering."""
    return [
        "apple",
        "banana",
        "cherry",
        "strawberry",
        "blueberry",
        "raspberry",
        "blackberry",
        "peach",
        "plum",
        "grape",
        "mango",
        "papaya",
        "pineapple",
        "watermelon",
        "orange",
        "lemon",
        "lime",
        "tangerine",
        "car",  # Outlier
        "bicycle",  # Outlier
    ]


@pytest.fixture
def test_texts() -> list[str]:
    """A list of test texts for testing outlier and representative filtering."""
    return [
        "apple",
        "banana",
        "kiwi",
        "fig",
        "apricot",
        "grapefruit",
        "pomegranate",
        "motorcycle",  # Outlier
        "plane",  # Outlier
    ]
