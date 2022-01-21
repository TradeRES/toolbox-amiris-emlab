from datetime import datetime, timedelta

now = datetime.now()

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            +timedelta(hours=t.minute//30))

print(now)
print(hour_rounder(now))