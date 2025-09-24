from collections import defaultdict

from dotenv import load_dotenv
from icecream import ic
# import numpy as np
# from sentence_transformers import util

from .common import InternMatchDetail
from .models.app_models import Intern, Supervisor
# from .matching_ml_model import get_model
from .settings import settings

load_dotenv()

# def embed_skills(skills: list[str]):
#     if not skills:
#         return np.zeros(get_model().get_sentence_embedding_dimension())
#     embeddings = get_model().encode(skills, convert_to_tensor=True)
#     return embeddings.mean(dim=0)  # average embedding of skills
#
# def ml_similarity(
#         intern_vec: np.ndarray = None, supervisor_vec: np.ndarray = None
# ):
#     """
#     The core of calculating matches.
#     """
#     return util.cos_sim(intern_vec, supervisor_vec).item()

def skills_similarity(intern_skills: list, supervisor_skills: list, method: str = "jaccard"):
    intern_set = set(intern_skills)
    supervisor_set = set(supervisor_skills)
    overlap = len(intern_set & supervisor_set)

    if not intern_set or not supervisor_set:
        return 0

    if method == "intern_ratio":
        return overlap / len(intern_set)
    elif method == "supervisor_ratio":
        return overlap / len(supervisor_set)
    else:  # default to Jaccard
        return overlap / len(intern_set | supervisor_set)

def match_interns_to_supervisors(supervisors_list: list, interns_list: list):
    matches_ = defaultdict(list)  # supervisor_id -> list of intern_ids

    # if settings.USE_ML_MATCHING:
    #     supervisor_skill_embedding_dict = {
    #         supervisor["id"]: embed_skills(supervisor["skills"])
    #         for supervisor in supervisors_list
    #     }
    #     intern_skill_embedding_dict = {
    #         intern["id"]: embed_skills(intern["skills"])
    #         for intern in interns_list
    #     }

    for intern in interns_list:
        best_supervisor = None
        best_score = -1
        for supervisor in supervisors_list:
            score = skills_similarity(intern["skills"], supervisor["skills"])


            if score > best_score:
                best_score = score
                best_supervisor = supervisor["id"]

        if best_supervisor is not None:
            matches_[best_supervisor].append(InternMatchDetail(intern_id=intern["id"], similarity=best_score))

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
            "firstname": supervisor.user.firstname,
            "lastname": supervisor.user.lastname,
            "department": supervisor.user.department.name,
            "skills": [skill.name for skill in supervisor.skills],
        }
        for supervisor in supervisors
    ]

    interns_details: list[dict[str, int | str | list[str]]] = [
        {
            "id": str(intern.id),
            "firstname": intern.user.firstname,
            "lastname": intern.user.lastname,
            "department": intern.user.department.name,
            "skills": [skill.name for skill in intern.skills],
        }
        for intern in interns
    ]

    matches = run_matching(supervisors_details, interns_details)
    ic(matches)
    return matches
