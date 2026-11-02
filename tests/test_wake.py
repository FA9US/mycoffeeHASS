"""Exercise the scheduled wake protocol without a network connection."""
import json
from types import SimpleNamespace
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components/delonghi_aromatic"))

from aromatic_cloud.account import CheckError, owned_machine
from aromatic_cloud.wake import ACKNOWLEDGED, wake_once


class WakeTests(unittest.TestCase):
    def exercise(self, state="Idle", reply_id=None, denied=False, retained_status=False):
        client = Mock()
        mqtt = Mock(MQTT_ERR_SUCCESS=0)
        good = SimpleNamespace(is_failure=False)
        bad = SimpleNamespace(is_failure=True)
        commands = []

        def deliver(topic, data, retained=False):
            msg = SimpleNamespace(topic=topic, payload=json.dumps(data).encode(), retain=retained)
            client.on_message(client, None, msg)

        def publish(topic, payload, **options):
            body = json.loads(payload)
            if topic.endswith("/get"):
                status = {"clientToken": body["clientToken"], "state": {"reported": {"Status": state}}}
                deliver(topic + "/accepted", status, retained_status)
                deliver(topic + "/accepted", status, retained_status)
            else:
                commands.append(body)
                self.assertEqual(topic, "fixture/commands/request")
                self.assertEqual(body["TurnOnOff"], 2)
                self.assertEqual((body["Message"], body["AppId"]), ("MachineUI", "MCL"))
                self.assertEqual(options["qos"], 1)
                self.assertFalse(options["retain"])
                self.assertEqual(options["properties"].MessageExpiryInterval, 15)
                deliver("fixture/commands/response", {"Message": "MachineUIResponse",
                        "Response": "OK", "RequestId": reply_id or body["RequestId"]})
            return SimpleNamespace(rc=0)

        def loop(timeout):
            client.on_connect(client, None, None, good, None)
            client.on_subscribe(client, None, 1, [bad if denied else good, good, good], None)
            return 1  # Simulate disconnect after deliveries, never retry.

        client.loop.side_effect = loop
        client.subscribe.return_value = (0, 1)
        client.publish.side_effect = publish
        result = wake_once("fixture", "fixture-token", lambda token: (mqtt, client))
        client.disconnect.assert_called_once()
        return result, len(commands)

    def test_single_wake_on_duplicate_status(self):
        self.assertEqual(self.exercise(), (ACKNOWLEDGED, 1))

    def test_active_and_denied_do_not_send(self):
        self.assertEqual(self.exercise(state="Heating")[1], 0)
        self.assertEqual(self.exercise(denied=True)[1], 0)

    def test_unrelated_reply_cannot_confirm_wake(self):
        result, count = self.exercise(reply_id="unrelated")
        self.assertIn("unknown", result)
        self.assertEqual(count, 1)

    def test_other_machine_cannot_be_used(self):
        with self.assertRaises(CheckError):
            owned_machine({"ownedByMe": [{"serialNumber": "different", "machineName": "fixture"}]}, "test-serial")

    def test_missing_serial_cannot_match_incomplete_record(self):
        with self.assertRaises(CheckError):
            owned_machine({"ownedByMe": [{"machineName": "fixture"}]}, " ")

    def test_retained_status_cannot_trigger_a_command(self):
        self.assertEqual(self.exercise(retained_status=True)[1], 0)


if __name__ == "__main__":
    unittest.main()
