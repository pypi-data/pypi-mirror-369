from astropilot import AstroPilot, Journal

folder = "Project_chemist6"

# set AstroPilot and input text
astro_pilot = AstroPilot(project_dir=folder)
astro_pilot.set_data_description(f"{folder}/input.md")

# Generate a research idea from the input text
#astro_pilot.get_idea_fast(llm='gemini-2.5-flash')

# Generate a research plan to carry out the idea
#astro_pilot.get_method_fast(llm="gemini-2.5-pro")

# Follow the research plan, write and execute code, make plots, and summarize the results
#astro_pilot.get_results(engineer_model='gemini-2.5-pro', researcher_model='gemini-2.5-pro')
#astro_pilot.get_results()

# Write a paper with [APS (Physical Review Journals)](https://journals.aps.org/) style
astro_pilot.get_paper(journal=Journal.AAS, llm='gemini-2.5-flash', add_citations=True)



