import datetime
import os
import site
from importlib import import_module, reload
from zoneinfo import ZoneInfo

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db.migrations.recorder import MigrationRecorder

from django_zero_migrations_commands import settings as local_settings


class Command(BaseCommand):
    help = "Resets the migration history and creates or applies new initial migrations."

    def call(self, *args: str) -> None:
        """
        Call a management command with the given arguments.
        Prints the command to the console before executing it.
        """
        self.stdout.write(" ".join(("python", "manage.py") + args), self.style.WARNING)
        call_command(*args)

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            nargs=1,
            type=str,
            choices=["create", "apply"],
            help="The action to perform.",
        )

    def handle(self, *args, **options):
        """
        Reset the migration history and create or apply new initial migrations.
        """
        self.action = options["action"][0]

        self.getapps()
        self.stdout.write(
            f"{self.action} zero migrations for {self.apps}", self.style.WARNING
        )

        if self.action == "create":
            if not settings.DEBUG:
                if not local_settings.ALLOW_CREATE_DEBUG_FALSE:
                    raise CommandError(
                        "This command can only be run with settings.DEBUG = True."
                    )
                if (
                    local_settings.CONFIRM_CREATE_DEBUG_FALSE
                    and input(
                        "Are you sure you want to run this command in production mode? [y/N] >>> "
                    ).lower()
                    != "y"
                ):
                    raise CommandError("Aborted.")

            if local_settings.BEFORE_CREATE_HOOK:
                local_settings.BEFORE_CREATE_HOOK()

            # 1. reset the migration history and delete the migration files
            for app in self.apps:
                MigrationRecorder.Migration.objects.filter(app=app).delete()
                os.system(f"rm -rf {app}/migrations/*")

            # 2. create new initial migration files
            for app in self.apps:
                self.call("makemigrations", app)

            self.stdout.write("Migrations created successfully.", self.style.SUCCESS)

        elif self.action == "apply":
            if not settings.DEBUG:
                if not local_settings.ALLOW_APPLY_DEBUG_FALSE:
                    raise CommandError(
                        "This command can only be run with settings.DEBUG = True."
                    )
                if (
                    local_settings.CONFIRM_APPLY_DEBUG_FALSE
                    and input(
                        "Are you sure you want to run this command in production mode? [y/N] >>> "
                    ).lower()
                    != "y"
                ):
                    raise CommandError("Aborted.")

            # The new migrations can be applied by first clearing the migration history and then adding them to the migration history
            for app in self.apps:
                MigrationRecorder.Migration.objects.filter(app=app).delete()
                MigrationRecorder.Migration.objects.create(
                    app=app,
                    name="0001_initial",
                    applied=datetime.datetime.now(ZoneInfo("UTC")),
                )

            self.stdout.write("Migrations applied successfully.", self.style.SUCCESS)

    def getapps(self) -> None:
        """
        Get the apps to reset migrations for.
        If `ZERO_MIGRATIONS_APPS` is set in the django settings file, use that.
        Otherwise, get all local apps. Local apps are apps that are not installed in the site-packages directory.
        """
        if local_settings.APPS is not None:
            self.apps = local_settings.APPS
            return

        sitepackagespath = str(site.getsitepackages()[0])
        self.apps = [
            app.name
            for app in apps.get_app_configs()
            if not str(app.path).startswith(sitepackagespath)
        ]
