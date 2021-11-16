from workspace.util.application_runner import ApplicationRunner

from . import Application


def main():
    runner = ApplicationRunner("archive_extractor")
    application = Application()
    runner.run(application)


if __name__ == "__main__":
    main()
