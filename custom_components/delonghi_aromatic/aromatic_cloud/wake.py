"""One explicit wake request on the owned Aromatic."""
import json
import re
import secrets
import string
import time

from .transport import HOST, mqtt_client

ACKNOWLEDGED = "Machine acknowledged this wake request. Physically verify warm-up or rinse."


def wake_once(machine, jwt, client_factory=mqtt_client):
    if not isinstance(machine, str) or not re.fullmatch(r"[A-Za-z0-9:_-]{1,128}", machine):
        return "Unexpected machine name. Wake skipped."
    mqtt, c = client_factory(jwt)
    nonce = secrets.token_hex(12)
    request_id = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(5))
    status = f"$aws/things/{machine}/shadow/name/MachineStatus/get"
    response = machine + "/commands/response"
    result = None
    sent = False

    def connected(client, _, flags, reason, props):
        nonlocal result
        if reason.is_failure:
            result = f"Broker refused sign-in (code {reason.value}). Wake skipped."
        elif client.subscribe([(response, 1), (status+"/accepted", 1), (status+"/rejected", 1)])[0] != mqtt.MQTT_ERR_SUCCESS:
            result = "Subscriptions failed. Wake skipped."

    def subscribed(client, _, mid, reasons, props):
        nonlocal result
        if len(reasons) != 3 or any(r.is_failure for r in reasons):
            result = "Could not subscribe to status and replies. Wake skipped."
        elif client.publish(status, json.dumps({"clientToken": nonce}), qos=1).rc != mqtt.MQTT_ERR_SUCCESS:
            result = "Could not request cloud status. Wake skipped."

    def received(client, _, msg):
        nonlocal result, sent
        if result is not None or msg.retain or len(msg.payload) > 131072:
            return
        try:
            body = json.loads(msg.payload)
        except (ValueError, UnicodeError):
            return
        if not isinstance(body, dict):
            return
        if msg.topic == response and sent and body.get("RequestId") == request_id and body.get("Message") == "MachineUIResponse":
            result = (ACKNOWLEDGED
                      if body.get("Response") == "OK" else "Machine did not acknowledge success. No retry.")
        elif not sent and body.get("clientToken") == nonce:
            if msg.topic == status + "/rejected":
                result = "Cloud status read refused. Wake skipped."
            elif msg.topic == status + "/accepted":
                state = body.get("state")
                reported = state.get("reported") if isinstance(state, dict) else None
                value = reported.get("Status") if isinstance(reported, dict) else None
                if not isinstance(value, str) or value.lower() not in {"idle", "standby", "off"}:
                    result = "Expected resting status was not reported. Wake skipped."
                    return
                # Idle is ambiguous. Always use explicit ON and never toggle.
                payload = {"AppId":"MCL", "Message":"MachineUI", "TurnOnOff":2, "RequestId":request_id}
                expiry = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
                expiry.MessageExpiryInterval = 15
                sent = True
                info = client.publish(machine + "/commands/request", json.dumps(payload),
                                      qos=1, retain=False, properties=expiry)
                if info.rc != mqtt.MQTT_ERR_SUCCESS:
                    result = "Could not confirm submission. No retry."

    c.on_connect, c.on_subscribe, c.on_message = connected, subscribed, received
    try:
        c.connect(HOST, 443, keepalive=20, clean_start=True)
        deadline = time.monotonic() + 30
        while result is None and time.monotonic() < deadline:
            if c.loop(timeout=0.5) != mqtt.MQTT_ERR_SUCCESS:
                break
        return result or ("Wake submitted; outcome unknown. No retry." if sent else "Wake was not sent.")
    except (OSError, ValueError, mqtt.WebsocketConnectionError):
        return "Connection failed. " + ("Wake outcome unknown. No retry." if sent else "Wake was not sent.")
    finally:
        c.disconnect()
