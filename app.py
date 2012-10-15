"""App that launches Photoshop from inside of Shotgun"""

import os
import tank
import platform

class LaunchPhotoshop(tank.platform.Application):
    def init_app(self):
        entity_types = self.get_setting("entity_types")
        deny_permissions = self.get_setting("deny_permissions")
        deny_platforms = self.get_setting("deny_platforms")

        p = {
            "title": "Launch Photoshop",
            "entity_types": entity_types,
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": False
        }

        self.engine.register_command("launch_photoshop", self.launch_photoshop, p)

    def _execute_app(self):
        """Executes the app in a platform specific fashion"""

        # add our startup path to the photoshop init path
        startup_path = os.path.abspath(os.path.join( os.path.dirname(__file__), "startup"))
        tank.util.append_path_to_env_var("PYTHONPATH", startup_path)

        # get the setting        
        system = platform.system()
        try:
            app_setting = {"Linux": "linux_path", "Darwin": "mac_path", "Windows": "windows_path"}[system]
            app_path = self.get_setting(app_setting)
            if not app_path: raise KeyError()
        except KeyError:
            raise Exception("Platform '%s' is not supported." % system)

        # run the app
        if system == "Darwin":
            cmd = 'open -n "%s"' % app_path
        elif system == "Windows":
            cmd = 'start /B "Photoshop" "%s"' % app_path
        else:
            raise Exception("Platform '%s' is not supported." % system)

        self.log_debug("Executing launch command '%s'" % cmd)
        exit_code = os.system(cmd)
        if exit_code != 0:
            self.log_error("Failed to launch Photoshop! This is most likely because the path "
                          "to the photoshop executable is not set to a correct value. The "
                          "current value is '%s' - please double check that this path "
                          "is valid and update as needed in this app's configuration. "
                          "If you have any questions, don't hesitate to contact support "
                          "on tanksupport@shotgunsoftware.com." % app_path)

    def launch_from_path(self, path):
        # Store data needed for bootstrapping Tank in env vars. Used in startup/menu.py
        os.environ["TANK_PHOTOSHOP_ENGINE"] = self.get_setting("engine")
        os.environ["TANK_PHOTOSHOP_PROJECT_ROOT"] = self.tank.project_path
        os.environ["TANK_PHOTOSHOP_FILE_TO_OPEN"] = path

        # now launch photoshop!
        self._execute_app()

    def launch_from_entity(self, entity_type, entity_id):
        engine = self.get_setting("engine")

        # Store data needed for bootstrapping Tank in env vars. Used in startup/userSetup.mel
        os.environ["TANK_PHOTOSHOP_ENGINE"] = engine
        os.environ["TANK_PHOTOSHOP_PROJECT_ROOT"] = self.tank.project_path
        os.environ["TANK_PHOTOSHOP_ENTITY_TYPE"] = entity_type
        os.environ["TANK_PHOTOSHOP_ENTITY_ID"] = str(entity_id)

        # now launch photoshop!
        self._execute_app()

    def launch_photoshop(self, entity_type, entity_ids):
        if len(entity_ids) != 1:
            raise Exception("LaunchPhotoshop only accepts a single entry in entity_ids.")

        entity_id = entity_ids[0]

        # Try to create path for the context.
        try:  
            self.tank.create_filesystem_structure(entity_type, entity_id)
        except tank.TankError, e:
            raise Exception("Could not create folders on disk. Error reported: %s" % e)            
        

        # kick off the app
        self.launch_from_entity(entity_type, entity_id)
