"""EU cloud MQTT transport."""
import ssl
import uuid

HOST = "a2612mo23mfrw1-ats.iot.eu-central-1.amazonaws.com"
AUTH = "x-amz-customauthorizer-name=dlg-prod-token-authorizer"


def mqtt_client(jwt):
    import paho.mqtt.client as mqtt

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="dlg-appliance-kit-android-" + str(uuid.uuid4()),
                         protocol=mqtt.MQTTv5, transport="websockets")
    client.connect_timeout = 6
    client.tls_set_context(ssl.create_default_context())
    client.ws_set_options(path="/mqtt?" + AUTH)
    client.username_pw_set(AUTH, jwt)
    return mqtt, client


