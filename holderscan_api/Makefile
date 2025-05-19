# Makefile برای HolderScan API

.PHONY: install run-examples run-advanced quick-check clean help

# نصب وابستگی‌ها
install:
	python3 -m venv venv
	source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ نصب کامل شد!"

# اجرای مثال‌های کلی
run-examples:
	source venv/bin/activate && python3 examples.py

# اجرای تحلیل پیشرفته
run-advanced:
	source venv/bin/activate && python3 advanced_analysis.py

# بررسی سریع (نیاز به آرگومان TOKEN_ADDRESS)
quick-check:
	@if [ -z "$(TOKEN)" ]; then \
		echo "❌ استفاده: make quick-check TOKEN=your_token_address"; \
	else \
		source venv/bin/activate && python3 quick_check.py $(TOKEN); \
	fi

# پاک‌سازی
clean:
	rm -rf venv/
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf *.png
	rm -rf *.xlsx
	@echo "✅ پاک‌سازی کامل شد!"

# راهنما
help:
	@echo "دستورات موجود:"
	@echo "  make install      - نصب وابستگی‌ها"
	@echo "  make run-examples - اجرای مثال‌های کلی"
	@echo "  make run-advanced - اجرای تحلیل پیشرفته"
	@echo "  make quick-check TOKEN=address - بررسی سریع توکن"
	@echo "  make clean        - پاک‌سازی فایل‌ها"
	@echo "  make help         - نمایش این راهنما"
