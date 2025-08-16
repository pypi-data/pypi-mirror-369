import json

import pytest
from httpx import HTTPStatusError

from pylon_client.client import PylonClient
from pylon_common.constants import (
    ENDPOINT_COMMITMENT,
    ENDPOINT_HYPERPARAMS,
    ENDPOINT_LATEST_BLOCK,
    ENDPOINT_SET_WEIGHT,
    endpoint_name,
)

MOCK_DATA_PATH = "./tests/mock_data.json"
MOCK_DATA = json.load(open(MOCK_DATA_PATH))


@pytest.fixture
def mock_pylon_client() -> PylonClient:
    """Fixture to set up the mock synchronous Pylon API environment."""
    client = PylonClient(mock_data_path=MOCK_DATA_PATH)
    assert client.mock is not None
    return client


def test_pylon_client_get_latest_block(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly get the latest block."""
    with mock_pylon_client as client:
        response = client.get_latest_block()
        assert response is not None
        assert response["block"] == MOCK_DATA["metagraph"]["block"]
    client.mock.latest_block.assert_called_once()  # type: ignore


def test_pylon_client_get_metagraph(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly get the metagraph."""
    with mock_pylon_client as client:
        response = client.get_metagraph()
        assert response is not None
        assert response.block == MOCK_DATA["metagraph"]["block"]
        assert len(response.neurons) == len(MOCK_DATA["metagraph"]["neurons"])
    client.mock.latest_metagraph.assert_called_with()  # type: ignore


def test_pylon_client_get_block_hash(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly get a block hash."""
    with mock_pylon_client as client:
        block = MOCK_DATA["metagraph"]["block"]
        response = client.get_block_hash(block)
        assert response is not None
        assert response["block_hash"] == MOCK_DATA["metagraph"]["block_hash"]
    client.mock.block_hash.assert_called_with(block=block)  # type: ignore


def test_pylon_client_get_epoch(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly get epoch information."""
    with mock_pylon_client as client:
        response = client.get_epoch()
        assert response is not None
        assert response.epoch_start == MOCK_DATA["epoch"]["epoch_start"]
        assert response.epoch_end == MOCK_DATA["epoch"]["epoch_end"]
    client.mock.epoch.assert_called_with(block=None)  # type: ignore


def test_pylon_client_get_hyperparams(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly get hyperparameters."""
    with mock_pylon_client as client:
        response = client.get_hyperparams()
        assert response is not None
        assert response == MOCK_DATA["hyperparams"]
    client.mock.hyperparams.assert_called_once()  # type: ignore


def test_pylon_client_set_hyperparam(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly set a hyperparameter."""
    with mock_pylon_client as client:
        response = client.set_hyperparam("tempo", 120)
        assert response is not None
        assert response["detail"] == "Hyperparameter set successfully"
    client.mock.set_hyperparam.assert_called_with(name="tempo", value=120)  # type: ignore


def test_pylon_client_get_weights(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly get weights."""
    with mock_pylon_client as client:
        response = client.get_weights()
        assert response is not None
        assert response == {"epoch": 1440, "weights": MOCK_DATA["weights"]}
    client.mock.weights.assert_called_with(block=None)  # type: ignore


def test_pylon_client_force_commit_weights(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can force commit weights."""
    with mock_pylon_client as client:
        response = client.force_commit_weights()
        assert response is not None
        assert response["detail"] == "Weights committed successfully"
    client.mock.force_commit_weights.assert_called_once()  # type: ignore


def test_pylon_client_get_commitment(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly get a commitment."""
    hotkey = "hotkey2"
    with mock_pylon_client as client:
        response = client.get_commitment(hotkey)
        assert response is not None
        expected = MOCK_DATA["commitments"][hotkey]
        assert response == {"commitment": expected, "hotkey": hotkey}
    client.mock.commitment.assert_called_with(hotkey=hotkey, block=None)  # type: ignore


def test_pylon_client_get_commitments(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly get all commitments."""
    with mock_pylon_client as client:
        response = client.get_commitments()
        assert response is not None
        assert response == MOCK_DATA["commitments"]
    client.mock.commitments.assert_called_with(block=None)  # type: ignore


def test_pylon_client_override_response(mock_pylon_client: PylonClient):
    """Tests that a default mock response can be overridden for a specific test."""
    new_block = 99999
    mock_pylon_client.override(endpoint_name(ENDPOINT_LATEST_BLOCK), {"block": new_block})  # type: ignore
    with mock_pylon_client as client:
        response = client.get_latest_block()
        assert response is not None
        assert response["block"] == new_block
    client.mock.latest_block.assert_called_once()  # type: ignore


def test_pylon_client_handles_error(mock_pylon_client: PylonClient):
    """Tests that the PylonClient correctly handles an error response from the server."""
    mock_pylon_client.override(  # type: ignore
        endpoint_name(ENDPOINT_LATEST_BLOCK), {"detail": "Internal Server Error"}, status_code=500
    )
    with mock_pylon_client as client:
        with pytest.raises(HTTPStatusError):
            client.get_latest_block()
    client.mock.latest_block.assert_called_once()  # type: ignore


def test_pylon_client_set_weight(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly set a weight."""
    with mock_pylon_client as client:
        response = client.set_weight("some_hotkey", 0.5)
        assert response is not None
        assert response["detail"] == "Weight set successfully"
    client.mock.set_weight.assert_called_with(hotkey="some_hotkey", weight=0.5)  # type: ignore


def test_pylon_client_set_weights(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly set multiple weights at once."""
    weights = {"hotkey1": 0.6, "hotkey2": 0.4}
    with mock_pylon_client as client:
        response = client.set_weights(weights)
        assert response is not None
        assert response["count"] == 2
        assert response["weights"]["hotkey1"] == 0.6
        assert response["weights"]["hotkey2"] == 0.4
        assert response["epoch"] == 1440
    client.mock.set_weights.assert_called_with(weights=weights)  # type: ignore


def test_pylon_client_update_weight(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly update a weight."""
    with mock_pylon_client as client:
        response = client.update_weight("some_hotkey", 0.1)
        assert response is not None
        assert response["detail"] == "Weight updated successfully"
    client.mock.update_weight.assert_called_with(hotkey="some_hotkey", weight_delta=0.1)  # type: ignore


def test_pylon_client_set_commitment(mock_pylon_client: PylonClient):
    """Tests that the PylonClient can correctly set a commitment."""
    with mock_pylon_client as client:
        response = client.set_commitment("0x1234")
        assert response is not None
        assert response["detail"] == "Commitment set successfully"
    client.mock.set_commitment.assert_called_with(data_hex="0x1234")  # type: ignore


def test_pylon_client_override_get_commitment(mock_pylon_client: PylonClient):
    """Tests that the get_commitment mock response can be overridden."""
    hotkey = "hotkey_override"
    commitment = "0xdeadbeef"
    mock_pylon_client.override(endpoint_name(ENDPOINT_COMMITMENT), {"hotkey": hotkey, "commitment": commitment})  # type: ignore
    with mock_pylon_client as client:
        response = client.get_commitment(hotkey)
        assert response is not None
        assert response["hotkey"] == hotkey
        assert response["commitment"] == commitment
    client.mock.commitment.assert_called_with(hotkey=hotkey, block=None)  # type: ignore


def test_pylon_client_override_set_weight(mock_pylon_client: PylonClient):
    """Tests that the set_weight mock response can be overridden."""
    mock_pylon_client.override(endpoint_name(ENDPOINT_SET_WEIGHT), {"detail": "Custom success message"})  # type: ignore
    with mock_pylon_client as client:
        response = client.set_weight("some_hotkey", 0.99)
        assert response is not None
        assert response["detail"] == "Custom success message"
    client.mock.set_weight.assert_called_with(hotkey="some_hotkey", weight=0.99)  # type: ignore


def test_pylon_client_override_error_response(mock_pylon_client: PylonClient):
    """Tests that an error response can be injected for any endpoint."""
    mock_pylon_client.override(endpoint_name(ENDPOINT_HYPERPARAMS), {"detail": "Forbidden"}, status_code=403)  # type: ignore
    with mock_pylon_client as client:
        with pytest.raises(HTTPStatusError) as exc_info:
            client.get_hyperparams()
        assert exc_info.value.response.status_code == 403
    client.mock.hyperparams.assert_called_once()  # type: ignore
