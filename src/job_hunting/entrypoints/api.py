from datetime import datetime
from dataclasses import asdict

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from job_hunting.domain import commands
from job_hunting import bootstrap, views
from job_hunting.adapters.scraper import JobScraper

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
bus = bootstrap.bootstrap()


@app.route("/api/jobs/extract", methods=["GET"])
def extract_job_details() -> tuple[Response, int]:
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        scraper = JobScraper()
        details = scraper.extract_from_url(url)
        # Using asdict for a simple dataclass
        return jsonify(details), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs", methods=["POST"])
def create_job() -> tuple[Response, int]:
    data = request.get_json()
    cmd = commands.CreateJobApplication(
        company=data["company"],
        position=data["position"],
        url=data.get("url"),
        status=data.get("status", "Applied"),
        date_applied=datetime.fromisoformat(data["date_applied"])
        if data.get("date_applied")
        else None,
        salary=data.get("salary"),
        salary_estimated=data.get("salary_estimated", False),
    )
    bus.handle(cmd)
    return jsonify("OK"), 201

@app.route("/api/jobs/<int:job_id>/status", methods=["PUT"])
def update_job_status(job_id: int) -> tuple[Response, int]:
    data = request.get_json()
    cmd = commands.UpdateJobApplicationStatus(
        job_id=job_id,
        status=data["status"]
    )
    updated_job = bus.handle(cmd)
    if not updated_job:
        return jsonify({"message": "Job not found"}), 404
    return jsonify("OK"), 200


@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id: int) -> tuple[Response, int]:
    cmd = commands.DeleteJobApplication(job_id=job_id)
    bus.handle(cmd)
    return jsonify("OK"), 200

@app.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id: int) -> tuple[Response, int]:
    result = views.view_job_by_id(job_id, bus.uow)
    if not result:
        return jsonify({"message": "Job not found"}), 404
    return jsonify(result), 200

@app.route("/api/jobs", methods=["GET"])
def get_jobs() -> tuple[Response, int]:
    query_params = request.args
    jobs = views.list_jobs(query_params, bus.uow)
    return jsonify(jobs), 200
