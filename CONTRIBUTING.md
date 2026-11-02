# Contributing

Bug reports and pull requests are welcome. Include the Blender version, extension version, OS, exact menu path, expected result and the final traceback line. Reduce failures to a small scene when possible; do not upload private assets or credentials.

Use Blender 4.5-compatible Python/RNA/node interfaces. Blender 5.2.3 LTS is the currently tested runtime, not a guarantee for future releases. Document approximations instead of claiming numerical X4D parity.

Rebuild original public icons with:

```text
python scripts/build_icons.py
```

Run relevant tests in an isolated Blender user profile:

```text
blender --background --factory-startup --python-exit-code 1 --python tests/registration_test.py
blender --background --factory-startup --python-exit-code 1 --python tests/v060_test.py
blender --background --factory-startup --python-exit-code 1 --python tests/all_routes_test.py
blender --background --factory-startup --python-exit-code 1 --python tests/extended_test.py
```

Build and validate:

```text
blender --command extension build --source-dir x4d_workflow --output-dir dist
blender --command extension validate dist/x4d_workflow-0.6.1.zip
```

All contributions must be compatible with GPL-3.0-or-later. Do not contribute extracted proprietary icons, copied X4D code, credentials or personal screenshots.
