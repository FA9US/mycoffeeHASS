# mycoffeeHASS

I spent more than €1,500 on a De’Longhi PrimaDonna Aromatic. All I wanted was for it to turn on and warm up before I came downstairs. I couldn’t set a morning start time. My Samsung showed the machine, but my iPhone showed an empty profile with the same login. I tried sharing it with a new account. The invitation arrived and the machine never appeared. I contacted support and didn’t get a response.

So I vibe-coded the feature I wanted. The moment the machine actually turned on from standby was the reason to share this. If you have the same machine, here’s the source, my morning schedule, and the prompt to reproduce it.

## What worked on my machine

I physically confirmed a direct cloud request woke my **PrimaDonna Aromatic ECAM630.75.TSM** using My Coffee Lounge’s EU service. Home Assistant Core 2026.10.4 accepted my owner login, and I verified both morning triggers were enabled. I still need to observe the first scheduled wake. This public version asks for your serial number so it can verify that your owner account controls the intended machine. Compatibility with other models, regions, social sign-in and shared accounts is unverified.

The action is **Warm up**. Start-up can include a hot-water rinse. My weekday start time is **06:45** and my weekend start time is **08:45**, both in Home Assistant’s local time. Brewing is outside the scope of the integration.

## Install

1. Pair the machine in My Coffee Lounge with a working phone (i only had luck with unrooted samsungs. no i phones...). Have the serial number from its **More info** screen and the De’Longhi email/password login that owns it. Verify remote power-on from standby works with the app.
2. Get the EU app client ID once. If you have the official Android app’s base APK, install the Android SDK Build Tools, put `aapt2` on your PATH and run `python tools/app_client_id.py /path/to/base.apk` locally. On Windows you can pass `--aapt2 C:\path\to\aapt2.exe`. The printed value is the public app identifier. You can use the same identifier with HA even if your daily phone is an iPhone. The helper needs neither your phone connected nor your account password. [Android Asset Packaging Tool](https://developer.android.com/tools/aapt2)
3. In HACS, open **Custom repositories**, add this repository’s URL as type **Integration**, then download **mycoffeeHASS**. Alternatively, copy `custom_components/delonghi_aromatic/` into your HA configuration’s `custom_components/` folder. If you already have that component folder, compare it before replacing it. [HACS integration layout](https://www.hacs.xyz/docs/publish/integration/)
4. Restart Home Assistant, then choose **Settings → Devices & services → Add integration → PrimaDonna Aromatic**. Enter your serial, app client ID and De’Longhi owner login privately in HA. Setup verifies ownership. HA stores the login in its configuration entry so it can request a fresh short-lived token each morning.
5. With the machine in standby and the spouts clear for rinsing, run **PrimaDonna Aromatic → Warm up** once from Developer Tools → Actions. Check that the machine actually powers on. If you get an uncertain result, check the machine before making another request.
6. Create an empty HA automation, choose **Edit in YAML**, paste the example, save it, then check the enabled switch and your HA timezone. At the next scheduled time, compare the automation trace with the physical result. [Morning automation](examples/morning-warmup.yaml)

The command depends on the EU cloud being reachable. Each wake checks the last reported machine status. `Idle` can also describe a machine that is already awake. The action sends explicit ON, uses a short expiry, matches the machine’s reply to the request, and makes no application-level retry after a lost reply. A missed clock trigger while HA is offline is skipped.

## Reproduce or remove it

Run `python -m unittest discover -s tests` for the offline protocol checks. For the instructions to recreate the design and test it on your own machine, see the [reproduction prompt](REPRODUCE.md). To pause the routine, disable the morning automation. For full removal, delete that automation, remove the integration entry, remove the component through HACS or delete its folder, and restart HA.

This is an independent community project.
