"""Testing the supervisor service class methods"""

from collections import defaultdict

from dotenv import load_dotenv

from .models.app_models import Intern, Supervisor

load_dotenv()


def skills_similarity(intern_skills: list, supervisor_skills: list):
    """
    The core of calculating matches.
    Checks the percentage similarity of two sets of skills if there are any overlap
    """
    intern_set = set(intern_skills)
    supervisor_set = set(supervisor_skills)
    overlap = len(intern_set & supervisor_set)
    return overlap / len(intern_set) if intern_set else 0


def match_interns_to_supervisors(supervisors_list: list, interns_list: list):
    matches_ = defaultdict(list)  # supervisor_id -> list of intern_ids

    for intern in interns_list:
        best_supervisor = None
        best_score = -1
        for supervisor in supervisors_list:
            score = skills_similarity(intern["skills"], supervisor["skills"])
            if score > best_score:
                best_score = score
                best_supervisor = supervisor["id"]

        if best_supervisor is not None:
            matches_[best_supervisor].append(intern["id"])

    return dict(matches_)


def run_matching(all_supervisors, all_interns):
    results = {}
    # collating all department as a union set of all departments
    departments = set(
        [s["department"] for s in all_supervisors]
        + [i["department"] for i in all_interns]
    )

    for dept in departments:
        # Performing matching by department to ensure only people of the same department gets matched
        supervisors_ = [s for s in all_supervisors if s["department"] == dept]
        interns_ = [i for i in all_interns if i["department"] == dept]
        results[dept] = match_interns_to_supervisors(supervisors_, interns_)

    return results


def matcher(supervisors: list[Supervisor], interns: list[Intern]):
    # Expected data structure for matching
    supervisors_details: list[dict[str, int | str | list[str]]] = [
        {
            "id": str(supervisor.id),
            "department": supervisor.user.department.name,
            "skills": [skill.name for skill in supervisor.skills],
        }
        for supervisor in supervisors
    ]

    interns_details: list[dict[str, int | str | list[str]]] = [
        {
            "id": str(intern.id),
            "department": intern.user.department.name,
            "skills": [skill.name for skill in intern.skills],
        }
        for intern in interns
    ]

    matches = run_matching(supervisors_details, interns_details)
    return matches
