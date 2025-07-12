#!/bin/bash
cd "$(dirname "$0")"/../..
source venv/bin/activate  # Adjust to your virtualenv path

# Run Python command to delete inactive customers
deleted_count=$(python manage.py shell -c "
from datetime import datetime, timedelta
from crm.models import Customer
one_year_ago = datetime.now() - timedelta(days=365)
qs = Customer.objects.filter(orders__isnull=True, created__lte=one_year_ago)
count = qs.count()
qs.delete()
print(count)
")

echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $deleted_count" >> /tmp/customer_cleanup_log.txt
