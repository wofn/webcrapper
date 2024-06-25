import csv
def save_to_file(keyword, jobs_db):
    file = open(f"{keyword}_jobs.csv", "w")
    writer = csv.writer(file)
    writer.writerow(["Title", "Company", "Reward", "Link"])

    for job in jobs_db:
        writer.writerow(job.values())
    file.close()