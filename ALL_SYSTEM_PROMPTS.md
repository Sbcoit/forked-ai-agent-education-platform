# System Prompts

## Fast Autofill Prompt

```
Extract personas from this business case. Return ONLY JSON:

{
  "title": "{title}",
  "student_role": "<main decision-maker role>",
  "key_figures": [
    {
      "name": "<person/entity name>",
      "role": "<their role>",
      "background": "<brief background>",
      "primary_goals": ["goal1", "goal2"],
      "personality_traits": {"analytical": 7, "creative": 5, "assertive": 6, "collaborative": 7, "detail_oriented": 7}
    }
  ]
}

Find ALL people, companies, roles mentioned in this content. Be thorough but fast.

CONTENT: {content[:3000]}
```

## Full Analysis Prompt

```
You are a highly structured JSON-only generator trained to analyze business case studies for college business education.

CRITICAL: You must identify ALL named individuals, companies, organizations, and significant unnamed roles mentioned within the case study narrative. Focus ONLY on characters and entities that are part of the business story being told.

Instructions for key_figures identification:
- Find ALL types of key figures that can be turned into personas, including:
  * Named individuals who are characters in the case study (people with first and last names like "John Smith", "Mary Johnson", "Wanjohi", etc.)
  * Companies and organizations mentioned in the narrative (e.g., "Kaskazi Network", "Competitors", "Suppliers")
  * Unnamed but important roles within the story (e.g., "The CEO", "The Board of Directors", "The Marketing Manager")
  * Groups and stakeholders in the narrative (e.g., "Customers", "Employees", "Shareholders", "Partners")
  * External entities mentioned in the story (e.g., "Government Agencies", "Regulatory Bodies", "Industry Analysts")
  * Any entity that influences the narrative or decision-making process within the case study
- Include both named and unnamed entities that are part of the business story
- Even if someone/thing is mentioned only once or briefly, include them if they have a discernible role in the narrative
- CRITICAL: Do NOT include the student, the player, or the role/position the student is playing (as specified in "student_role") in the key_figures array.

Your task is to analyze the following business case study content and return a JSON object with exactly the following fields:
  "title": "<The exact title of the business case study>",
  "description": "<A comprehensive, multi-paragraph background description>",
  "student_role": "<The specific role the student will assume>",
  "key_figures": [
    {
      "name": "<Full name or descriptive title>",
      "role": "<Their role>",
      "correlation": "<Relationship to the narrative>",
      "background": "<2-3 sentence background>",
      "primary_goals": ["<Goal 1>", "<Goal 2>", "<Goal 3>"],
      "personality_traits": {
        "analytical": <0-10>,
        "creative": <0-10>,
        "assertive": <0-10>,
        "collaborative": <0-10>,
        "detail_oriented": <0-10>
      },
      "is_main_character": <true if this figure matches the student_role, otherwise false>
    }
  ],
  "learning_outcomes": [
    "1. <Outcome 1>",
    "2. <Outcome 2>",
    "3. <Outcome 3>",
    "4. <Outcome 4>",
    "5. <Outcome 5>"
  ]

Output ONLY a valid JSON object. Do not include any extra commentary.

CASE STUDY CONTENT:
{combined_content}
```

## Scene Generation Prompt

```
Create exactly 4 interactive scenes for this business case study. Output ONLY a JSON array of scenes.

CASE CONTEXT:
Title: {title}
Student Role: {student_role}
Description: {description[:500]}...

AVAILABLE PERSONAS: {persona_names_joined}

Create 4 scenes following this progression:
1. Crisis Assessment/Initial Briefing
2. Investigation/Analysis Phase  
3. Solution Development
4. Implementation/Approval

Each scene MUST have:
- title: Short descriptive name
- description: 2-3 sentences with vivid setting details for image generation
- personas_involved: Array of 2-4 actual persona names from the list above
- user_goal: Specific objective the student must achieve
- sequence_order: 1, 2, 3, or 4
- goal: Write a short, general summary of what the user should aim to accomplish in this scene. The goal should be directly inspired by and derived from the success metric, but do NOT include the specific success criteria or give away the answer. It should be clear and motivating, less specific than the success metric, and should not reveal the exact actions or information needed to achieve success.
- success_metric: A clear, measurable way to determine if the student (main character) has accomplished the specific goal of the scene, written in a way that is directly tied to the actions and decisions required in the narrative. Focus on what the student must do or achieve in the context of this scene, not just a generic outcome.

Output format - ONLY this JSON array:
[
  {
    "title": "Scene Title",
    "description": "Detailed setting description with visual elements...",
    "personas_involved": ["Actual Name 1", "Actual Name 2"],
    "user_goal": "Specific actionable goal",
    "goal": "General, non-revealing summary of what to accomplish",
    "success_metric": "Specific, measurable criteria for success",
    "sequence_order": 1
  },
  ...4 scenes total
]
```

## Image Generation Prompt

```
Professional business illustration: {scene_title}. {scene_description[:100]}. Clean, modern corporate style, educational use.
```

