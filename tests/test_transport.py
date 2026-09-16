from engine.protocol import Protocol
from network.transport import JsonTransport


def test_encode_returns_bytes():
    message = Protocol.roll()

    encoded = JsonTransport.encode(
        message
    )

    assert isinstance(encoded, bytes)


def test_encoded_message_ends_with_newline():
    message = Protocol.roll()

    encoded = JsonTransport.encode(
        message
    )

    assert encoded.endswith(b"\n")


def test_encode_decode_round_trip():
    message = Protocol.move(
        pawn_id=16,
        row=5,
        col=8
    )

    encoded = JsonTransport.encode(
        message
    )

    decoded = JsonTransport.decode(
        encoded
    )

    assert decoded == message


def test_decode_accepts_string():
    message = Protocol.roll()

    encoded = JsonTransport.encode(
        message
    ).decode("utf-8")

    decoded = JsonTransport.decode(
        encoded
    )

    assert decoded == message


def test_decode_rejects_invalid_json():
    decoded = JsonTransport.decode(
        b"not-json\n"
    )

    assert decoded is None


def test_decode_rejects_empty_message():
    assert JsonTransport.decode(
        b"\n"
    ) is None


def test_decode_rejects_json_list():
    decoded = JsonTransport.decode(
        b"[1,2,3]\n"
    )

    assert decoded is None


def test_multiple_messages_have_clear_boundaries():
    first = JsonTransport.encode(
        Protocol.roll()
    )

    second = JsonTransport.encode(
        Protocol.create_room()
    )

    combined = first + second

    lines = combined.splitlines()

    assert len(lines) == 2

    assert (
        JsonTransport.decode(lines[0])
        == Protocol.roll()
    )

    assert (
        JsonTransport.decode(lines[1])
        == Protocol.create_room()
    )