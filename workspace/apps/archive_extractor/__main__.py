from workspace.util.application_runner import ApplicationRunner
from . import Application

runner = ApplicationRunner("archive_extractor")
application = Application()
runner.run(application)
