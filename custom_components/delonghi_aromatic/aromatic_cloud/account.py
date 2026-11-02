"""Sign in and resolve only the owned Aromatic."""
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

LOGIN = "https://accounts.eu1.gigya.com/accounts.login"
CLOUD = "https://8q8c9xktb0.execute-api.eu-central-1.amazonaws.com/dlg-prod/"


class CheckError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def fetch(request, stage):
    try:
        with build_opener(NoRedirect()).open(request, timeout=15) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise CheckError(f"{stage}: HTTP {exc.code}.") from None
    except (OSError, ValueError):
        raise CheckError(f"{stage}: could not reach the service or read its response.") from None
    if not isinstance(result, dict):
        raise CheckError(f"{stage}: unexpected response format.")
    return result


def rows(body, key):
    value = body.get(key)
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise CheckError("Unexpected device or invitation list format.")
    return value


def login_devices(email, password, client_key):
    fields = {"apiKey": client_key, "loginID": email, "password": password,
              "targetEnv": "mobile", "include": "id_token", "sessionExpiration": "300"}
    login = fetch(Request(LOGIN, data=urlencode(fields).encode()), "De’Longhi sign-in")
    if not login.get("id_token"):
        code = login.get("errorCode")
        raise CheckError("Sign-in did not return an ID token." +
                         (f" Service code {code}." if isinstance(code, int) else ""))
    headers = {"Authorization": "Bearer " + login["id_token"], "source": "mycoffeelounge"}
    devices = fetch(Request(CLOUD + "devices", headers=headers), "Device list")
    return login["id_token"], devices


def owned_machine(devices, serial):
    if not isinstance(serial, str) or not serial.strip():
        raise CheckError("Enter the serial shown on the machine.")
    matches = [item for item in rows(devices, "ownedByMe")
               if str(item.get("serialNumber", "")).strip() == serial.strip()]
    if len(matches) != 1 or not matches[0].get("machineName"):
        raise CheckError("No unique owned Aromatic with a cloud name was returned.")
    return matches[0]["machineName"]
