from ta5py import encode, decode, validate_syntax


def test_encode_decode_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    inputs = {
        "ik_sender": "123456789",
        "ik_receiver": "987654321",
        "leistungsdatum": "20260817",
        "km": 12,
        "positions": [{"code": "TAX1", "amount_cents": 2500}],
    }
    result = encode(inputs, "v20", output_dir=tmp_path)
    assert result.syntax_ok
    assert result.output_uri
    data = decode(result.output_uri, "v20")
    assert data["km"] == 12
    syntax = validate_syntax(result.output_uri, "v20")
    assert syntax.syntax_ok


def test_syntax_rejects_bad_ik(tmp_path):
    from ta5py.encode import encode

    result = encode(
        {
            "ik_sender": "bad",
            "ik_receiver": "987654321",
            "leistungsdatum": "20260817",
            "km": 1,
            "positions": [{"code": "A", "amount_cents": 1}],
        },
        "v20",
        output_dir=tmp_path,
    )
    assert not result.syntax_ok
