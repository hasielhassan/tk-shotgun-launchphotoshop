"""
This file is loaded automatically by Photoshop at startup
It sets up the tank context and prepares the Tank Photoshop engine.
"""


import os

def bootstrap_tank():
    try:
        import tank
    except Exception, e:
        os.system("""osascript -e 'tell app "Finder" to display dialog "Could not import Tank! Disabling Tank for now: Details: %s"'""" % e)
        return

    if not "TANK_PHOTOSHOP_ENGINE" in os.environ:
        os.system("""osascript -e 'tell app "Finder" to display dialog "Missing required environment variable TANK_PHOTOSHOP_ENGINE"'""")
        return

    engine_name = os.environ.get("TANK_PHOTOSHOP_ENGINE")
    file_to_open = os.environ.get("TANK_PHOTOSHOP_FILE_TO_OPEN")
    project_root = os.environ.get("TANK_PHOTOSHOP_PROJECT_ROOT")
    entity_id = int(os.environ.get("TANK_PHOTOSHOP_ENTITY_ID", "0"))
    entity_type = os.environ.get("TANK_PHOTOSHOP_ENTITY_TYPE")

    try:
        tk = tank.Tank(project_root)
    except Exception, e:
        os.system("""osascript -e 'tell app "Finder" to display dialog "The Tank API could not be initialized! Tank will be disabled. Details: %s"'""" % e)
        return

    try:
        if file_to_open:
            ctx = tk.context_from_path(file_to_open)
        else:
            ctx = tk.context_from_entity(entity_type, entity_id)
    except Exception, e:
        os.system("""osascript -e 'tell app "Finder" to display dialog "Could not determine the Tank Context! Disabling Tank for now. Details: %s"'""" % e)
        return

    try:
        engine = tank.platform.start_engine(engine_name, tk, ctx)
    except tank.TankEngineInitError, e:
        os.system("""osascript -e 'tell app "Finder" to display dialog "The Tank Engine could not start! Tank will be disabled. Details: %s"'""" % e)

    # clean up temp env vars
    if "TANK_PHOTOSHOP_ENGINE" in os.environ:
        del os.environ["TANK_PHOTOSHOP_ENGINE"]

    if "TANK_PHOTOSHOP_PROJECT_ROOT" in os.environ:
        del os.environ["TANK_PHOTOSHOP_PROJECT_ROOT"]

    if "TANK_PHOTOSHOP_ENTITY_ID" in os.environ:
        del os.environ["TANK_PHOTOSHOP_ENTITY_ID"]

    if "TANK_PHOTOSHOP_ENTITY_TYPE" in os.environ:
        del os.environ["TANK_PHOTOSHOP_ENTITY_TYPE"]

    if "TANK_PHOTOSHOP_FILE_TO_OPEN" in os.environ:
        del os.environ["TANK_PHOTOSHOP_FILE_TO_OPEN"]

    if file_to_open:
        os.system("""osascript -e 'tell app "Finder" to display dialog "Would open %s"'""" % file_to_open)
        # finally open the file
        # cmds.file(file_to_open, force=True, open=True)

# cmds.evalDeferred("bootstrap_tank()")
bootstrap_tank()
