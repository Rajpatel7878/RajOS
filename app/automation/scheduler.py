from datetime import datetime


class Scheduler:


    def __init__(self):

        self.jobs = []



    def add_job(
        self,
        automation_id: int,
        trigger_time: str
    ):

        job = {
            "automation_id": automation_id,
            "trigger_time": trigger_time,
            "created_at": datetime.now()
        }

        self.jobs.append(job)

        return {
            "status": "scheduled",
            "job": job
        }



    def list_jobs(self):

        return self.jobs



    def remove_job(
        self,
        automation_id: int
    ):

        self.jobs = [
            job for job in self.jobs
            if job["automation_id"] != automation_id
        ]

        return {
            "status": "removed",
            "automation_id": automation_id
        }



scheduler = Scheduler()
