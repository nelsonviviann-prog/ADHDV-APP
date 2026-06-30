"""
Vanderbilt-style ADHD questionnaire definitions, adapted from the NICHQ
Vanderbilt Assessment Scale (public domain). Two parallel forms: Parent
(home-context) and Teacher (classroom-context).

The 18 DSM-5 core symptom items are identical across forms; the wording of
the performance items differs (school subjects/peer relations for parent,
academic and behavioural performance for teacher).
"""

from __future__ import annotations

from dataclasses import dataclass

from . import config as cfg


@dataclass(frozen=True)
class Question:
    item_id: str
    prompt: str
    section: str  # 'inattention' | 'hyperactivity' | 'performance' | 'odd' | 'anxiety'
    scale: str    # 'likert' (0-4) | 'performance' (1-5)


# ---------------------------------------------------------------------------
# 18 DSM-5 core ADHD symptoms (identical wording across parent/teacher forms,
# only the lead-in instruction changes).
# ---------------------------------------------------------------------------

INATTENTION_QUESTIONS = [
    Question(cfg.INATTENTION_ITEMS[0], "Does not pay attention to details or makes careless mistakes (e.g., in schoolwork).", "inattention", "likert"),
    Question(cfg.INATTENTION_ITEMS[1], "Has difficulty sustaining attention to tasks or activities.", "inattention", "likert"),
    Question(cfg.INATTENTION_ITEMS[2], "Does not seem to listen when spoken to directly.", "inattention", "likert"),
    Question(cfg.INATTENTION_ITEMS[3], "Does not follow through on instructions and fails to finish schoolwork or chores.", "inattention", "likert"),
    Question(cfg.INATTENTION_ITEMS[4], "Has difficulty organising tasks and activities.", "inattention", "likert"),
    Question(cfg.INATTENTION_ITEMS[5], "Avoids, dislikes, or is reluctant to engage in tasks requiring sustained mental effort.", "inattention", "likert"),
    Question(cfg.INATTENTION_ITEMS[6], "Loses things necessary for tasks (school assignments, books, pencils).", "inattention", "likert"),
    Question(cfg.INATTENTION_ITEMS[7], "Is easily distracted by noises or other things going on around them.", "inattention", "likert"),
    Question(cfg.INATTENTION_ITEMS[8], "Is forgetful in daily activities.", "inattention", "likert"),
]

HYPERACTIVITY_QUESTIONS = [
    Question(cfg.HYPERACTIVITY_ITEMS[0], "Fidgets with hands or feet, or squirms in seat.", "hyperactivity", "likert"),
    Question(cfg.HYPERACTIVITY_ITEMS[1], "Leaves seat in the classroom or in other situations when remaining seated is expected.", "hyperactivity", "likert"),
    Question(cfg.HYPERACTIVITY_ITEMS[2], "Runs about or climbs excessively in situations where it is inappropriate.", "hyperactivity", "likert"),
    Question(cfg.HYPERACTIVITY_ITEMS[3], "Has difficulty playing or engaging in leisure activities quietly.", "hyperactivity", "likert"),
    Question(cfg.HYPERACTIVITY_ITEMS[4], "Is 'on the go' or acts as if 'driven by a motor.'", "hyperactivity", "likert"),
    Question(cfg.HYPERACTIVITY_ITEMS[5], "Talks excessively.", "hyperactivity", "likert"),
    Question(cfg.HYPERACTIVITY_ITEMS[6], "Blurts out answers before questions have been completed.", "hyperactivity", "likert"),
    Question(cfg.HYPERACTIVITY_ITEMS[7], "Has difficulty awaiting turn.", "hyperactivity", "likert"),
    Question(cfg.HYPERACTIVITY_ITEMS[8], "Interrupts or intrudes on others (e.g., into conversations or games).", "hyperactivity", "likert"),
]

# ---------------------------------------------------------------------------
# Co-occurring screens (brief, not diagnostic — flag for referral only).
# ---------------------------------------------------------------------------

ODD_QUESTIONS = [
    Question(cfg.ODD_ITEMS[0], "Loses temper.", "odd", "likert"),
    Question(cfg.ODD_ITEMS[1], "Actively argues with adults.", "odd", "likert"),
    Question(cfg.ODD_ITEMS[2], "Actively defies or refuses to comply with adults' requests or rules.", "odd", "likert"),
    Question(cfg.ODD_ITEMS[3], "Deliberately annoys people.", "odd", "likert"),
]

ANXIETY_QUESTIONS = [
    Question(cfg.ANXIETY_ITEMS[0], "Is fearful, anxious, or worried.", "anxiety", "likert"),
    Question(cfg.ANXIETY_ITEMS[1], "Has low self-esteem (puts themselves down).", "anxiety", "likert"),
    Question(cfg.ANXIETY_ITEMS[2], "Is sad, unhappy, or appears depressed.", "anxiety", "likert"),
]

# ---------------------------------------------------------------------------
# Performance/impairment items — wording differs between parent and teacher.
# Scored 1 (Excellent) to 5 (Problematic). Vanderbilt-aligned.
# ---------------------------------------------------------------------------

PERFORMANCE_QUESTIONS_PARENT = [
    Question(cfg.PERFORMANCE_ITEMS[0], "Overall school performance.",                                "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[1], "Reading.",                                                   "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[2], "Writing.",                                                   "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[3], "Mathematics.",                                               "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[4], "Relationship with parents.",                                  "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[5], "Relationship with brothers and sisters.",                     "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[6], "Relationship with peers.",                                    "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[7], "Participation in organised activities (sports, religious or community groups).", "performance", "performance"),
]

PERFORMANCE_QUESTIONS_TEACHER = [
    Question(cfg.PERFORMANCE_ITEMS[0], "Overall academic performance in your class.",                "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[1], "Reading.",                                                   "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[2], "Writing.",                                                   "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[3], "Mathematics.",                                               "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[4], "Classroom behaviour and following teacher instructions.",     "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[5], "Performance in group work.",                                  "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[6], "Relationship with classmates.",                              "performance", "performance"),
    Question(cfg.PERFORMANCE_ITEMS[7], "Organisational skills (notebooks, school materials).",        "performance", "performance"),
]


def parent_form() -> list[Question]:
    return (
        INATTENTION_QUESTIONS
        + HYPERACTIVITY_QUESTIONS
        + PERFORMANCE_QUESTIONS_PARENT
        + ODD_QUESTIONS
        + ANXIETY_QUESTIONS
    )


def teacher_form() -> list[Question]:
    return (
        INATTENTION_QUESTIONS
        + HYPERACTIVITY_QUESTIONS
        + PERFORMANCE_QUESTIONS_TEACHER
        + ODD_QUESTIONS
        + ANXIETY_QUESTIONS
    )


FORM_INTRO_PARENT = (
    "Thinking about your child's behaviour **over the past 6 months at home and in social "
    "settings**, indicate how often each of the following has been a concern."
)
FORM_INTRO_TEACHER = (
    "Thinking about this student's behaviour **over the past 6 months in your classroom**, "
    "indicate how often each of the following has been a concern."
)
