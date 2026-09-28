# Problem Statement: Exam-Aware Study Planner

## Background
Traditional spaced-repetition (SR) software (like Anki) uses algorithms such as SM-2 to schedule reviews based on memory decay. However, these systems are "open-ended" and unaware of fixed deadlines. For students, this creates a critical flaw: an SR algorithm might schedule the next review of a crucial topic for *after* the exam date, leading to memory decay right when recall is needed most.

## Objective
Develop a command-line study planning tool that implements standard spaced repetition (SM-2) but adds an **Exam Awareness** layer to compress intervals and guarantee optimal review timing prior to fixed test dates.

## Functional Requirements
1. **Topic Management**: Users can add, list, and delete study topics.
2. **Exam Deadlines**: Topics can optionally be tied to an exam date.
3. **Daily Scheduling**: The system must identify which topics are due for review "today".
4. **Spaced Repetition**: 
   - Uses an ease factor starting at 2.5.
   - User rates recall on a 0-5 scale.
   - Grades < 3 reset the topic's interval.
5. **Exam Compression**: If an exam date is set, the scheduled interval must not exceed half the remaining days to the exam, and the final review must fall exactly one day before the exam.

## Non-Functional Requirements
- **Standard Library Only**: Must run on standard Python 3.8+ without external dependencies (`pip install`).
- **Data Persistence**: State must be saved locally in a human-readable JSON format.
- **Stateless Logic**: Core scheduling logic must be decoupled from file I/O to enable unit testing.
