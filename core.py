from datetime import datetime

class Measure:
    def __init__(self, value: float):
        self.value = value
        self.timestamp = datetime.now()

class Series:
    def __init__(self):
        self.measures = []

    def add(self, value):
        self.measures.append(Measure(value))

    def summary(self):
        values = [m.value for m in self.measures]
        return {
            'count': len(values),
            'min': min(values) if values else None,
            'max': max(values) if values else None,
            'average': sum(values)/len(values) if values else None
        }