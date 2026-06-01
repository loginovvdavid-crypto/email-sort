import json
import logging
from collections import Counter
from datetime import datetime
logger = logging.getLogger(__name__)

class ProcessingRecord:
    def __init__(self, filename, category, confidence, reason, subject, sender):
        self.filename = filename
        self.category = category
        self.confidence = confidence
        self.reason = reason
        self.subject = subject
        self.sender = sender

class Report:
    def __init__(self):
        self.records = []
        self.category_counts = Counter()
        self.total = 0
        self.started_at = ""
        self.finished_at = ""

    def add(self, record):
        self.records.append(record)
        self.category_counts[record.category] += 1
        self.total += 1

    @property
    def errors(self):
        return self.category_counts.get("unknown", 0)

    @property
    def processed(self):
        return self.total - self.errors

class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def save(self, report):
        self._save_json(report)
        self._save_txt(report)

    def _save_json(self, report):
        data = {
            "started_at": report.started_at,
            "finished_at": report.finished_at,
            "total": report.total,
            "processed": report.processed,
            "errors": report.errors,
            "by_category": dict(report.category_counts),
            "records": [
                {
                    "filename": r.filename,
                    "category": r.category,
                    "confidence": r.confidence,
                    "subject": r.subject,
                    "sender": r.sender,
                }
                for r in report.records
            ],
        }
        path = self.output_dir / "report.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("JSON-отчёт сохранён: %s", path)

    def _save_txt(self, report):
        lines = []
        lines.append("=" * 60)
        lines.append("  ОТЧЁТ ОБРАБОТКИ ВХОДЯЩИХ ПИСЕМ")
        lines.append("=" * 60)
        lines.append(f"Начало:    {report.started_at}")
        lines.append(f"Конец:     {report.finished_at}")
        lines.append(f"Всего:     {report.total}")
        lines.append(f"Успешно:   {report.processed}")
        lines.append(f"Unknown:   {report.errors}")
        lines.append("")
        lines.append("Распределение по категориям:")
        lines.append("-" * 40)

        for cat, count in report.category_counts.most_common():
            pct = count / report.total * 100 if report.total else 0
            lines.append(f"  {cat:<22} {count:>3}  ({pct:.1f}%)")

        lines.append("")
        lines.append("Аналитические выводы:")
        lines.append("-" * 40)
        lines += self._get_insights(report)
        lines.append("")
        lines.append("Детали по каждому письму:")
        lines.append("-" * 40)

        for r in report.records:
            subj = r.subject[:45] if r.subject else "(без темы)"
            lines.append(f"  [{r.category:<18}] [{r.confidence:<6}] {r.filename}  {subj}")
        path = self.output_dir / "report.txt"
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Текстовый отчёт: %s", path)

    def _get_insights(self, report):
        insights = []
        total = report.total
        counts = report.category_counts
        if total == 0:
            return ["  Нет данных для анализа."]
        
        top_cat, top_count = counts.most_common(1)[0]
        insights.append(
            f"  - Больше всего писем в категории '{top_cat}': {top_count} ({top_count/total*100:.1f}%). "
            f"Это говорит о высокой нагрузке по данному направлению."
        )
        #Спам
        spam_count = counts.get("spam", 0)
        if spam_count > 0:
            insights.append(
                f"  - Спам составляет {spam_count/total*100:.1f}% входящих ({spam_count} писем). "
                f"Рекомендуется настроить спам-фильтр на уровне почтового сервера."
            )
        #Критические
        inc_count = counts.get("incidents", 0)
        if inc_count > 0:
            insights.append(
                f"  - Зафиксировано {inc_count} критических инцидентов ({inc_count/total*100:.1f}%). "
                f"Каждый такой запрос требует немедленной реакции — рекомендуется выделить дежурного."
            )
        #Письма без класа
        unknown_count = counts.get("unknown", 0)
        if unknown_count > 0:
            insights.append(
                f"  - {unknown_count} писем ({unknown_count/total*100:.1f}%) не удалось классифицировать. "
                f"Они сохранены в папку 'unknown' для ручной проверки."
            )
        #Доступы
        access_count = counts.get("access_requests", 0)
        if access_count > 0:
            insights.append(
                f"  - Запросы на доступ составляют {access_count/total*100:.1f}% — "
                f"рекомендуется автоматизировать выдачу стандартных прав для новых сотрудников."
            )
        return insights
