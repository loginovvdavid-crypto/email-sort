import logging
import sys
from datetime import datetime
from pathlib import Path
from src.email_classifier import EmailClassifier
from src.email_reader import EmailReader
from src.email_sorter import EmailSorter
from src.report import ProcessingRecord, Report, ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("processing.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

def main(inbox_dir="inbox", output_dir="output"):
    inbox_path = Path(inbox_dir)
    output_path = Path(output_dir)

    if not inbox_path.exists():
        logger.error("Папка inbox не найдена: %s", inbox_path)
        sys.exit(1)

    reader = EmailReader()
    classifier = EmailClassifier()
    sorter = EmailSorter(output_path)
    report = Report()
    report.started_at = datetime.now().isoformat(timespec="seconds")
    email_files = sorted(inbox_path.glob("*.txt"))
    logger.info("Найдено писем: %d", len(email_files))

    for file_path in email_files:
        email = reader.read(file_path)
        result = classifier.classify(email)
        sorter.sort(email, result)
        report.add(ProcessingRecord(
            filename=file_path.name,
            category=result.category,
            confidence=result.confidence,
            reason=result.reason,
            subject=email.subject,
            sender=email.sender,
        ))

    report.finished_at = datetime.now().isoformat(timespec="seconds")

    report_gen = ReportGenerator(output_path)
    report_gen.save(report)

    print("\n" + "=" * 50)
    print(f"Обработано писем: {report.total}")
    print("")
    for category, count in report.category_counts.most_common():
        print(f"  {category:<22} {count}")
    print("=" * 50)
    print(f"Отчёт: {output_path / 'report.txt'}")

if name == "__main__":
    inbox = sys.argv[1] if len(sys.argv) > 1 else "inbox"
    output = sys.argv[2] if len(sys.argv) > 2 else "output"
    main(inbox, output)