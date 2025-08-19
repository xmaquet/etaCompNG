import csv

def export_csv(series, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Value'])
        for measure in series.measures:
            writer.writerow([measure.timestamp, measure.value])