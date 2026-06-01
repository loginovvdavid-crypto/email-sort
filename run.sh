#!/bin/bash
INBOX_DIR="${1:-inbox}"
OUTPUT_DIR="${2:-output}"
LOG_FILE="processing.log"

echo "=== Email Sorting System ==="
echo "Inbox:  $INBOX_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

if [ ! -d "$INBOX_DIR" ]; then
    echo "ERROR: Папка '$INBOX_DIR' не найдена."
    exit 1
fi

EMAIL_COUNT=$(find "$INBOX_DIR" -maxdepth 1 -name "*.txt" | wc -l)
echo "Найдено писем: $EMAIL_COUNT"

if [ "$EMAIL_COUNT" -eq 0 ]; then
    echo "Нет писем для обработки."
    exit 0
fi

python main.py "$INBOX_DIR" "$OUTPUT_DIR" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

echo ""
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✓ Обработка завершена успешно."
    echo "  Отчёт: $OUTPUT_DIR/report.txt"
    echo "  Лог:   $LOG_FILE"
else
    echo "✗ Обработка завершена с ошибкой (код: $EXIT_CODE)."
fi

exit $EXIT_CODE