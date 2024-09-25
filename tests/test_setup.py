import xml.etree.ElementTree as ET
from unittest import mock

import pytest
import responses

import config
import src.downloader.setup as downloader
from sample_data import xml_samples
from src.downloader.setup import extract_graph_data


@pytest.fixture
def download_graph_ok(monkeypatch):
    monkeypatch.setattr(downloader, 'download_graph', lambda: xml_samples['valid'])


@pytest.fixture
def download_graph_fail(monkeypatch):
    monkeypatch.setattr(downloader, 'download_graph', lambda: None)


@pytest.fixture
def verify_graph_data_ok(monkeypatch):
    monkeypatch.setattr(downloader, 'verify_graph_data', lambda _: (True, None))


@pytest.fixture
def verify_graph_data_fail(monkeypatch):
    monkeypatch.setattr(downloader, 'verify_graph_data', lambda _: (False, None))


@pytest.fixture
def extract_graph_data_ok(monkeypatch):
    monkeypatch.setattr(downloader, 'extract_graph_data',
                        lambda _: ("g0", "Name", [("a", "A name")], [("e1", "a", "a", 42)]))


@pytest.fixture
def extract_graph_data_duplicate_node(monkeypatch):
    monkeypatch.setattr(downloader, 'extract_graph_data',
                        lambda _: ("g0", "Name", [("a", "A name"), ("a", "A name")], [("e1", "a", "a", 42)]))


@pytest.fixture
def extract_graph_data_duplicate_edge(monkeypatch):
    monkeypatch.setattr(downloader, 'extract_graph_data',
                        lambda _: ("g0", "Name", [("a", "A name")], [("e1", "a", "a", 42), ("e1", "a", "a", 42)]))


def test_set_up_graph_data_problem_downloading(download_graph_fail, capsys):
    # Simulate a failed download
    downloader.set_up_graph_data()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Problem downloading graph data."


def test_set_up_graph_data_problem_validating(download_graph_ok, verify_graph_data_fail, capsys):
    # Simulate a successful download but failed validation
    downloader.set_up_graph_data()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Problem validating graph data."


def test_set_up_graph_data_problem_unique_node_ids(
        download_graph_ok, verify_graph_data_ok, extract_graph_data_duplicate_node, capsys):
    # Simulate successful download and validation but failed unique node IDs
    downloader.set_up_graph_data()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Problem validating unique node IDs."


def test_set_up_graph_data_problem_unique_edge_ids(
        download_graph_ok, verify_graph_data_ok, extract_graph_data_duplicate_edge, capsys):
    # Simulate successful download and validation but failed unique node IDs
    downloader.set_up_graph_data()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Problem validating unique edge IDs."


def test_set_up_graph_data_problem_graph_id_exists(
        download_graph_ok, verify_graph_data_ok, extract_graph_data_ok, monkeypatch, capsys):
    # Simulate successful download, validation, unique nodes, but graph ID already exists
    monkeypatch.setattr(downloader, 'set_graph_id', lambda _: None)
    monkeypatch.setattr(downloader, 'graph_id_exists', lambda _: True)
    downloader.set_up_graph_data()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Graph ID already exists."


def test_set_up_graph_data_success(
        download_graph_ok, verify_graph_data_ok, extract_graph_data_ok, monkeypatch, capsys):
    # Simulate successful download, validation, unique nodes, and successful insert
    monkeypatch.setattr(downloader, 'set_graph_id', lambda _: None)
    monkeypatch.setattr(downloader, 'graph_id_exists', lambda _: False)
    monkeypatch.setattr(downloader, 'insert_graph_data', lambda _: None)
    downloader.set_up_graph_data()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Graph data successfully inserted."


@responses.activate
def test_download_graph_ok():
    responses.add(
        responses.GET,
        config.graph_data_endpoint,
        body=xml_samples["valid"],
    )
    result = downloader.download_graph()
    assert result == xml_samples["valid"]


@responses.activate
def test_download_graph_not_found():
    responses.add(
        responses.GET,
        config.graph_data_endpoint,
        status=404,
    )
    result = downloader.download_graph()
    assert result is None


@responses.activate
def test_download_graph_server_error():
    responses.add(
        responses.GET,
        config.graph_data_endpoint,
        status=500,
    )
    result = downloader.download_graph()
    assert result is None


def test_verify_graph_data():
    for name, xml_sample in xml_samples.items():
        expected_result = False if "invalid" in name else True
        result, _ = downloader.verify_graph_data(xml_sample)
        assert result == expected_result


def test_extract_graph_data():
    graph_data = ET.fromstring(xml_samples["valid"])
    gid, name, nodes, edges = extract_graph_data(graph_data)
    assert gid == "g0"
    assert name == "Name"
    assert nodes == [("a", "A name")]
    assert edges == [("e1", "a", "a", 42)]


@pytest.mark.parametrize("xml_graph", [
    xml_samples["valid empty cost"],
    xml_samples["valid neg cost"],
    xml_samples["valid no cost"], ])
def test_extract_graph_data_empty_cost(xml_graph):
    graph_data = ET.fromstring(xml_graph)
    gid, name, nodes, edges = extract_graph_data(graph_data)
    assert gid == "g0"
    assert name == "Name"
    assert nodes == [("a", "A name")]
    assert edges == [("e1", "a", "a", 0)]


def test_verify_unique_node_ids():
    nodes = [("a", "A"), ("b", "B"), ("c", "C")]
    result = downloader.verify_unique_ids(nodes)
    assert result is True

    nodes = [("a", "A"), ("b", "B"), ("a", "C")]
    result = downloader.verify_unique_ids(nodes)
    assert result is False

    nodes = [("a", "A"), ("b", "B"), ("c", "C"), ("a", "D")]
    result = downloader.verify_unique_ids(nodes)
    assert result is False


def test_set_graph_id(monkeypatch):
    mock_file = mock.mock_open()
    monkeypatch.setattr("builtins.open", mock_file)

    downloader.set_graph_id("graph_123")
    mock_file().write.assert_called_once_with("graph_123")
