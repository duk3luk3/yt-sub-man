from usersettings import Settings

settings = Settings('de.lerlacher.apps.ytsubman')

s = settings

s.add_setting('subfiles', list, [])
s.load_settings()
