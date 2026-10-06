import json

import pytest

import app
import wss_engine


def capture(ssid="LAB", bssid="02:11:22:33:44:55", auth="WPA2-Personal", cipher="CCMP", signal=70):
    return f"""SSID 1 : {ssid}
    Autenticacion : {auth}
    Cifrado : {cipher}
    BSSID 1 : {bssid}
        Senal : {signal}%
        Canal : 6
"""


@pytest.mark.parametrize("auth,cipher,score,classification", [
    ("WPA3-Personal", "CCMP", 1.0, "BAJO"),
    ("WPA2-Personal", "CCMP", 2.0, "BAJO"),
    ("WPA-Personal", "TKIP", 7.5, "ALTO"),
    ("Abierta", "Ninguna", 10.0, "CRITICO"),
    ("Abierta", "WEP", 9.5, "CRITICO"),
])
def test_thesis_acceptance_scenarios_from_capture_through_exports(auth, cipher, score, classification):
    response = app.process_raw_output(capture(auth=auth, cipher=cipher), app.SOURCE_FILE_IMPORT, "Caso sintético", synthetic_data=True)
    result = response["results"][0]
    assert result["wss_score"] == score
    assert result["classification"] == classification
    assert result["wss_vector"] == f"WSS:2.0/AU:{result['au']}/EN:{result['en']}"
    assert not {"ex", "an", "bm", "anomaly"}.intersection(result)
    report = app.build_report(response["results"], response["metadata"])
    exported = json.loads(json.dumps(report))["results"][0]
    assert exported["wss_score"] == score
    assert exported["wss_vector"] == result["wss_vector"]
    assert not {"ex", "an", "bm", "anomaly"}.intersection(exported)
    pdf = app.build_pdf_report(response["results"], response["metadata"])
    assert pdf["ok"]
    assert "Versión del esquema WSS: 2.0" in pdf["visible_text"]
    assert "AU / EN (pesos 50% / 50%)" in pdf["visible_text"]


@pytest.mark.parametrize("signal", [0, 20, 60, 100])
def test_signal_does_not_change_score(signal):
    assert wss_engine.evaluate_networks(capture(signal=signal))[0]["wss_score"] == 2.0


def test_alignment_does_not_change_score(monkeypatch):
    monkeypatch.setattr(wss_engine, "determine_bm", lambda *args: "DEVIANT")
    result = wss_engine.evaluate_networks(capture())[0]
    assert result["bm_label"] == "DEVIANT"
    assert result["wss_score"] == 2.0


@pytest.mark.parametrize("score,expected", [(2.5, "BAJO"), (2.51, "MEDIO"), (5.0, "MEDIO"), (5.01, "ALTO"), (7.5, "ALTO"), (7.51, "CRITICO")])
def test_classification_boundaries(score, expected):
    assert wss_engine.classify_score(score) == expected


@pytest.mark.parametrize("bssid", ["", "desconocido", "02:11:22", "00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"])
def test_invalid_radio_does_not_create_hidden_network(bssid):
    assert wss_engine.evaluate_networks(capture(ssid="", bssid=bssid)) == []


def test_real_hidden_observation_is_kept_and_deduplicated():
    raw = capture(ssid="")
    results = wss_engine.evaluate_networks(raw + raw)
    assert len(results) == 1
    assert results[0]["hidden_ssid"]
    assert results[0]["bssid"] == "02:11:22:33:44:55"


def test_hidden_header_without_radio_does_not_create_result():
    assert wss_engine.evaluate_networks("SSID 1 :\n Autenticacion : WPA2-Personal\n Cifrado : CCMP") == []


def test_literal_hidden_placeholder_name_is_visible():
    result = wss_engine.evaluate_networks(capture(ssid="(SSID oculto)"))[0]
    assert result["hidden_ssid"] is False
    assert result["ssid"] == "(SSID oculto)"


@pytest.mark.parametrize("hidden_first", [True, False])
def test_named_radio_replaces_hidden_copy_in_same_capture(hidden_first):
    parts = [capture(ssid=""), capture()]
    results = wss_engine.evaluate_networks("\n".join(parts if hidden_first else reversed(parts)))
    assert len(results) == 1
    assert results[0]["ssid"] == "LAB"
    assert not results[0]["hidden_ssid"]


def test_different_security_profile_is_not_silently_discarded():
    results = wss_engine.evaluate_networks(capture(ssid="") + capture(auth="Abierta", cipher="Ninguna"))
    assert len(results) == 2
    assert sum(item["hidden_ssid"] for item in results) == 1


def test_two_hidden_radios_remain_separate():
    raw = capture(ssid="") + capture(ssid="", bssid="02:11:22:33:44:66")
    response = app.process_raw_output(raw, app.SOURCE_FILE_IMPORT, "Caso sintético", synthetic_data=True)
    assert len(app.group_logical_networks(response["results"])) == 2
    assert {r["ssid"] for r in response["results"]} == {"SSID oculto 1", "SSID oculto 2"}


def test_failed_rescan_clears_previous_exportable_results(monkeypatch):
    api = app.WssApi()
    monkeypatch.setattr(wss_engine, "run_netsh_scan", lambda: capture(ssid=""))
    assert api.scan_networks()["ok"]
    def fail():
        raise RuntimeError("Captura no disponible")
    monkeypatch.setattr(wss_engine, "run_netsh_scan", fail)
    assert not api.scan_networks()["ok"]
    assert api.last_results == []
    assert api.last_metadata is None
    assert not api.export_json()["ok"]


def test_empty_rescan_does_not_retain_hidden_network(monkeypatch):
    api = app.WssApi()
    monkeypatch.setattr(wss_engine, "run_netsh_scan", lambda: capture(ssid=""))
    assert api.scan_networks()["results"]
    monkeypatch.setattr(wss_engine, "run_netsh_scan", lambda: "Hay 0 redes disponibles actualmente.")
    response = api.scan_networks()
    assert response["ok"]
    assert response["results"] == api.last_results == []
