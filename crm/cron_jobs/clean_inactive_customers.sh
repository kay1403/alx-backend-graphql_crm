#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
cd "$DIR"

if [ -f "manage.py" ]; then
    deleted_count=$(python3 manage.py shell -c "
from datetime import datetime, timedelta
from crm.models import Customer
one_year_ago = datetime.now() - timedelta(days=365)
qs = Customer.objects.filter(orders__isnull=True, created__lte=one_year_ago)
count = qs.count()
qs.delete()
print(count)
")
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $deleted_count" >> /tmp/customer_cleanup_log.txt
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: manage.py not found in $DIR" >> /tmp/customer_cleanup_log.txt
fi
