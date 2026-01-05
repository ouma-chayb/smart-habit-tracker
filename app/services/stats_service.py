from datetime import date, timedelta

def calculate_progress(habit):
    """Retourne le nombre total de jours où l'habitude a été réalisée"""
    total_days = len(habit["progress"])
    return {
        "total_days": total_days
    }

def calculate_streak(progress):
    """Calcule le streak actuel (jours consécutifs) d'une habitude"""
    if not progress:
        return 0

    dates = sorted(progress, reverse=True)
    streak = 0
    today = date.today()

    for d in dates:
        d_date = date.fromisoformat(d)
        if streak == 0:
            if d_date == today:
                streak = 1
                prev_date = d_date
            elif d_date == today - timedelta(days=1):
                streak = 1
                prev_date = d_date
            else:
                break
        else:
            if prev_date - d_date == timedelta(days=1):
                streak += 1
                prev_date = d_date
            else:
                break

    return streak

