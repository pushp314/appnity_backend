import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Create database backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Directory to store backup files',
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        
        # Create backup directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'appnity_backup_{timestamp}.sql'
        backup_path = os.path.join(output_dir, backup_filename)
        
        try:
            # Get database settings
            db_settings = settings.DATABASES['default']
            
            if db_settings['ENGINE'] == 'django.db.backends.postgresql':
                self.backup_postgresql(db_settings, backup_path)
            elif db_settings['ENGINE'] == 'django.db.backends.sqlite3':
                self.backup_sqlite(db_settings, backup_path)
            else:
                self.stdout.write(
                    self.style.ERROR(f'Unsupported database engine: {db_settings["ENGINE"]}')
                )
                return

            self.stdout.write(
                self.style.SUCCESS(f'✅ Database backup created: {backup_path}')
            )
            
            # Show backup file size
            file_size = os.path.getsize(backup_path)
            self.stdout.write(f'📊 Backup size: {file_size / 1024 / 1024:.2f} MB')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Backup failed: {str(e)}')
            )

    def backup_postgresql(self, db_settings, backup_path):
        """Create PostgreSQL backup using pg_dump"""
        cmd = [
            'pg_dump',
            '--host', db_settings['HOST'],
            '--port', str(db_settings['PORT']),
            '--username', db_settings['USER'],
            '--dbname', db_settings['NAME'],
            '--no-password',
            '--verbose',
            '--clean',
            '--no-owner',
            '--no-privileges',
            '--file', backup_path
        ]
        
        # Set password via environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        subprocess.run(cmd, env=env, check=True)

    def backup_sqlite(self, db_settings, backup_path):
        """Create SQLite backup"""
        import shutil
        shutil.copy2(db_settings['NAME'], backup_path)