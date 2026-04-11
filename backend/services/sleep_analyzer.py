"""
Dream Decoder - Sleep Analyzer
Computes sleep quality and emotion-based disturbance risk.
"""


class SleepAnalyzer:
    """Service for sleep quality scoring and disturbance prediction."""

    def __init__(self):
        self.ideal_sleep = {
            "duration_min": 7.0,
            "duration_max": 9.0,
            "interruptions_max": 1,
            "target_sleep_time": "23:00",
        }
        self.quality_weights = {
            "duration": 0.30,
            "quality_rating": 0.30,
            "interruptions": 0.20,
            "consistency": 0.20,
        }

    def calculate_sleep_quality(self, sleep_data):
        """Calculate weighted sleep quality score from user-reported data."""
        scores = {}

        duration = float(sleep_data.get("duration_hours", 7.0) or 7.0)
        if self.ideal_sleep["duration_min"] <= duration <= self.ideal_sleep["duration_max"]:
            scores["duration"] = 100
        elif duration < self.ideal_sleep["duration_min"]:
            scores["duration"] = max(0, 100 - (self.ideal_sleep["duration_min"] - duration) * 20)
        else:
            scores["duration"] = max(0, 100 - (duration - self.ideal_sleep["duration_max"]) * 15)

        quality_rating = int(sleep_data.get("quality_rating", 5) or 5)
        quality_rating = max(1, min(10, quality_rating))
        scores["quality"] = (quality_rating / 10) * 100

        interruptions = int(sleep_data.get("interruptions", 0) or 0)
        if interruptions <= self.ideal_sleep["interruptions_max"]:
            scores["interruptions"] = 100
        else:
            scores["interruptions"] = max(0, 100 - (interruptions - 1) * 25)

        consistency_score = self._calculate_consistency_score(sleep_data.get("sleep_time", "23:00"))
        scores["consistency"] = consistency_score

        total_score = (
            scores["duration"] * self.quality_weights["duration"]
            + scores["quality"] * self.quality_weights["quality_rating"]
            + scores["interruptions"] * self.quality_weights["interruptions"]
            + scores["consistency"] * self.quality_weights["consistency"]
        )

        return {
            "overall_score": round(total_score, 1),
            "breakdown": scores,
            "grade": self._score_to_grade(total_score),
        }

    def predict_sleep_disturbance(self, dream_emotions):
        """Estimate disturbance risk from dream emotion intensity."""
        high_risk_emotions = {"fear", "anxiety", "nervousness", "anger", "sadness", "grief"}

        risk_score = 0.0
        risk_factors = []

        for emotion, score in (dream_emotions or {}).items():
            emotion_key = str(emotion).strip().lower()
            score_value = float(score)
            if emotion_key in high_risk_emotions and score_value > 0.5:
                risk_score += score_value
                risk_factors.append({"emotion": emotion_key, "score": round(score_value, 3)})

        risk_probability = min(risk_score / 3.0, 1.0)

        if risk_probability < 0.3:
            risk_level = "Low"
        elif risk_probability < 0.6:
            risk_level = "Moderate"
        else:
            risk_level = "High"

        return {
            "risk_level": risk_level,
            "probability": round(risk_probability, 2),
            "risk_factors": risk_factors,
        }

    def _calculate_consistency_score(self, sleep_time):
        """Score bedtime consistency around target of 23:00."""
        try:
            target_minutes = self._time_to_minutes(self.ideal_sleep["target_sleep_time"])
            current_minutes = self._time_to_minutes(sleep_time)
            difference = abs(current_minutes - target_minutes)
            if difference > 720:
                difference = 1440 - difference

            if difference <= 30:
                return 100
            if difference <= 60:
                return 85
            if difference <= 120:
                return 65
            if difference <= 180:
                return 45
            return 25
        except Exception:
            return 60

    @staticmethod
    def _time_to_minutes(time_str):
        parts = str(time_str).split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        return hour * 60 + minute

    @staticmethod
    def _score_to_grade(score):
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"
