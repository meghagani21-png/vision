def get_roadmap(career_title, metadata):
    """Dynamically generates a learning roadmap based on core and bonus skills."""
    
    if career_title not in metadata:
        return [("Error", "No roadmap data available for this role.")]
        
    core = ", ".join(metadata[career_title]["core_skills"])
    bonus = ", ".join(metadata[career_title]["bonus_skills"])
    
    roadmap = [
        (
            "Phase 1: Foundation & Core Skills",
            f"**Goal:** Master the absolute essentials for this role.\n\n"
            f"**Focus Areas:** {core}\n\n"
            f"**Action Item:** Build 2 small projects focusing heavily on these core concepts. Don't move on until you are comfortable building without tutorials."
        ),
        (
            "Phase 2: Advanced Tools & Ecosystem",
            f"**Goal:** Learn the tools that make you highly employable.\n\n"
            f"**Focus Areas:** {bonus}\n\n"
            f"**Action Item:** Integrate these bonus tools into your Phase 1 projects. For example, if you learned a language, now deploy it to the cloud or add CI/CD."
        ),
        (
            "Phase 3: Real-World Architecture & Interview Prep",
            f"**Goal:** Prove your competence to employers.\n\n"
            f"**Action Item:** \n"
            f"- Build one massive, end-to-end capstone project.\n"
            f"- Create a well-documented GitHub repository.\n"
            f"- Practice LeetCode/HackerRank or domain-specific interview questions."
        )
    ]
    
    return roadmap