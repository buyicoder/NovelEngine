"""Project phase detection and transitions."""

VALID_PHASES = ["init", "worldbuilding", "outlining", "generating", "complete"]


def get_current_phase(project_root):
    from data_modules.config import load_project_state
    state = load_project_state(project_root)
    return state.get("project_info", {}).get("phase", "init")


def set_phase(project_root, new_phase):
    if new_phase not in VALID_PHASES:
        raise ValueError(f"Invalid phase: {new_phase}. Valid: {VALID_PHASES}")
    from data_modules.config import load_project_state, save_project_state
    state = load_project_state(project_root)
    if "project_info" not in state:
        state["project_info"] = {}
    old_phase = state["project_info"].get("phase", "init")
    state["project_info"]["phase"] = new_phase
    save_project_state(project_root, state)
    return old_phase, new_phase
