from datetime import datetime

class Habit:
    def __init__(self, name, progress=None, streak=0, record=0, days_missed=0, last_done=None):
        self.name = name
        self.progress = progress or []
        self.streak = streak
        self.record = record
        self.days_missed = days_missed
        self.last_done = last_done

    def mark_done(self, date_str):
        if date_str in self.progress:
            return

        self.progress.append(date_str)
        self.update_streak(date_str)

    def update_streak(self, date_str):
        today = datetime.strptime(date_str, "%Y-%m-%d").date()

        if self.last_done:
            last = datetime.strptime(self.last_done, "%Y-%m-%d").date()
            delta = (today - last).days

            if delta == 1:
                self.streak += 1
            elif delta > 1:
                self.days_missed += delta - 1
                self.streak = 1
        else:
            self.streak = 1

        self.last_done = date_str

        if self.streak > self.record:
            self.record = self.streak

    def get_motivation(self):
        if self.streak == 0:
            return "Commence aujourd’hui 💪"
        if self.streak < 3:
            return "Bon début 👏"
        if self.streak < 7:
            return "Continue comme ça 🔥"
        if self.streak < self.record:
            return f"Tu es à {self.record - self.streak} jour(s) de ton record 🔥"
        if self.streak == self.record and self.streak >= 7:
            return "Tu égalises ton record 🏆"
        if self.streak > self.record:
            return "NOUVEAU RECORD 🔥💪"
        if self.days_missed > 0:
            return "Un petit effort aujourd’hui fait la différence 💪"
        return "Habitude installée 🏆"

    def get_badge(self):
        if self.streak >= 30:
            return "🥇 Légende"
        if self.streak >= 14:
            return "🥈 Champion"
        if self.streak >= 7:
            return "🥉 Sérieux"
        if self.streak >= 3:
            return "🔥 En forme"
        return "🎯 Débutant"

    def get_success_rate(self):
        if not self.progress:
            return 0
        total = len(self.progress) + self.days_missed
        return round((len(self.progress) / total) * 100, 1)

    def to_dict(self):
        return {
            "name": self.name,
            "progress": self.progress,
            "streak": self.streak,
            "record": self.record,
            "days_missed": self.days_missed,
            "last_done": self.last_done
        }

