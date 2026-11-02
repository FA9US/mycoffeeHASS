# Reproduction prompt

Copy this prompt into your coding assistant. Use the repository’s source for exact wire details and dependency versions.

> Build a Home Assistant custom integration called mycoffeeHASS for my De’Longhi PrimaDonna Aromatic ECAM630.75.TSM. My appliance uses the My Coffee Lounge EU app. I want it to turn on and warm up at 06:45 Monday through Friday and 08:45 Saturday and Sunday, using Home Assistant’s local timezone.
>
> Start with this repository’s `custom_components/delonghi_aromatic/` directory and its morning automation. Keep the domain `delonghi_aromatic` and expose the single action `delonghi_aromatic.warm_up`. Ask for the owner’s serial number, the public EU app client ID and De’Longhi email/password inside HA. Verify the signed-in account lists exactly one matching serial under `ownedByMe`. Never copy my login or machine identifier into the repository, prompts, logs or screenshots.
>
> Reuse the HTTP authentication and MQTT v5 WebSocket transport from the source. Require TLS verification and a successful subscription to replies and the named MachineStatus shadow. Read the shadow with a nonce and verify it. Only send ON for a reported Idle, Standby or Off state. Idle can be ambiguous. Publish one non-retained QoS 1 request with AppId MCL, Message MachineUI, TurnOnOff 2, a fresh five-character alphanumeric RequestId and a 15-second expiry. Match MachineUIResponse, RequestId and OK. Treat a missing reply as an uncertain physical outcome. Do not send an OFF, toggle or brew command.
>
> Use fake clients to test success, denied status access, duplicate and retained events, unrelated replies, wrong serial and an already-active machine. Check both weekday lists and the exact times. Keep the installation reversible and stop for private sign-in. Validate a single attended wake before enabling my schedule. Report separately what was simulated, what the cloud acknowledged, what someone saw on the machine and whether an actual scheduled run completed. Scope claims to the EU region and model actually tested.
