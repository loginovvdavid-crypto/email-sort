import shutil
import logging

logger = logging.getLogger(__name__)
ALL_CATEGORIES = [
    "incidents",
    "access_requests",
    "hardware",
    "software",
    "documents",
    "hr",
    "monitoring",
    "newsletters",
    "spam",
    "unknown",
]

class EmailSorter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self._create_dirs()

    def _create_dirs(self):
        for category in ALL_CATEGORIES:
            folder = self.output_dir / category
            folder.mkdir(parents=True, exist_ok=True)

    def sort(self, email, result):
        target_dir = self.output_dir / result.category
        target_path = target_dir / email.path.name
        if target_path.exists():
            stem = email.path.stem
            suffix = email.path.suffix
            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
        try:
            shutil.copy2(email.path, target_path)
            logger.info("Скопировано %s -> %s", email.path.name, result.category)
        except OSError as e:
            logger.error("Ошибка при копировании %s: %s", email.path.name, e)
            target_path = self.output_dir / "unknown" / email.path.name
            shutil.copy2(email.path, target_path)

        return target_path
