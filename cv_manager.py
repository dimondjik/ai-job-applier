import logging

from pyhtml2pdf import converter
from airium import Airium
import os
from browser_client import BrowserClient
from config_manager import ConfigManager
from llm_client import LLMClient
import secrets
import string
from custom_types import *
# TODO: I really do no know when to throw that exception, here just for consistency
from custom_exceptions import (CVManagerException,  # noqa
                               CustomExceptionData)
import time

logger = logging.getLogger("CVManager")


class CVManager:
    def __init__(self):
        """
        A jumbled up class to generate resume
        """

        self.config = ConfigManager()

        self.exception_data = CustomExceptionData()

    def __convert_cv(self, html_path: str) -> str:
        """
        Converting generated html resume to pdf, return absolute path and filename

        :param html_path: Absolute path to the CV's html file

        :return: Absolute path to the CV's pdf file
        """

        logger.info(f"Converting CV to pdf...")

        pdf_resume_path = os.path.join(os.getcwd(), "generated_resume")
        pdf_resume_fname = (f"{self.config.user_info.personal.name}-"
                            f"{self.config.user_info.personal.surname}-"
                            f"{''.join(secrets.choice(string.ascii_uppercase) for _ in range(8))}"
                            f".pdf")

        converter.convert(f'file:///{html_path}', os.path.join(pdf_resume_path, pdf_resume_fname))

        return os.path.join(pdf_resume_path, pdf_resume_fname)

    def __generate_cv_html(self, llm_client: LLMClient, job_object: Job) -> str:
        """
        Generating html and filling it with LLM and local user data

        :param llm_client: LLM client instance to use
        :param job_object: Job object to tailor CV to

        :return: Absolute path to the CV's html file
        """

        # I can divide the HTML into
        # Left Side
        # - Title (name get from config, anything else - generate) +
        # - Work experience (generate) +
        # - Education (get from config) +
        # Right Side
        # - Contact information (get from config) +
        # - Hard Skills (generate) +
        # - Soft Skills (generate) +
        # - Languages (get from config) +
        # - Certifications and Courses (get from config) +

        # I think I'll just hardcode logging

        logger.info(f"Starting to generate CV for {job_object.title} ({job_object.company})")

        a = Airium(base_indent='    ')

        a('<!DOCTYPE html>')
        with a.html(lang='en'):
            # ----------------------------------------------------------------------------------------------------------
            # Metadata and CSS section
            # ----------------------------------------------------------------------------------------------------------
            with a.head():
                a.meta(charset='UTF-8')
                a.meta(content='width=device-width, initial-scale=1.0', name='viewport')
                a.meta(content='IE=edge', **{'http-equiv': 'X-UA-Compatible'})
                a.title(_t='The Resume')
                with a.style():
                    a('@import url(\'https://fonts.googleapis.com/css2?'
                      'family=Merriweather:wght@700&'
                      'family=Open+Sans:wght@400;700&'
                      'family=Open+Sans:ital,wght@0,400;1,400&'
                      'display=swap\');\n'
                      '            \n'
                      '            body {\n'
                      '                font-family: "Open Sans", sans-serif;\n'
                      '                margin: 0;\n'
                      '                padding: 20px;\n'
                      '                background-color: #ffffff;\n'
                      '            }\n'
                      '            .container {\n'
                      '                display: flex;\n'
                      '                justify-content: space-between;\n'
                      '                max-width: 960px;\n'
                      '                margin: 0 auto;\n'
                      '            }\n'
                      '            .left-column, .right-column {\n'
                      '                padding: 10px;\n'
                      '            }\n'
                      '            .left-column {\n'
                      '                width: 65%;\n'
                      '            }\n'
                      '            .right-column {\n'
                      '                width: 30%;\n'
                      '            }\n'
                      '            h1 {\n'
                      '            font-family: \'Merriweather\', serif;\n'
                      '                font-size: 28px;\n'
                      '                margin-bottom: 0;\n'
                      '                color: #000000;\n'
                      '            }\n'
                      '            h2, h3 {\n'
                      '                font-family: \'Merriweather\', serif;\n'
                      '                color: #9370DB;\n'
                      '            }\n'
                      '            h2 {\n'
                      '                font-size: 20px;\n'
                      '                margin-bottom: 10px;\n'
                      '            }\n'
                      '            h3 {\n'
                      '                font-size: 16px;\n'
                      '                margin-bottom: 5px;\n'
                      '            }\n'
                      '            p, li {\n'
                      '                font-family: \'Open Sans\', sans-serif;\n'
                      '                font-size: 12px;\n'
                      '                line-height: 1.4;\n'
                      '                color: #696969;\n'
                      '            }\n'
                      '            .section {\n'
                      '                margin-bottom: 15px;\n'
                      '            }\n'
                      '            .contact-info p, .contact-info a {\n'
                      '                font-size: 12px;\n'
                      '                margin-bottom: 5px;\n'
                      '                color: #696969;\n'
                      '            }\n'
                      '            ul {\n'
                      '                list-style-type: none;\n'
                      '                padding: 0;\n'
                      '            }\n'
                      '            ul li {\n'
                      '                margin-bottom: 8px;\n'
                      '            }\n'
                      '            a {\n'
                      '                color: #696969;\n'
                      '                text-decoration: none;\n'
                      '            }\n'
                      '            .subheading {\n'
                      '                font-family: \'Open Sans\', sans-serif;\n'
                      '                font-weight: bold;\n'
                      '                color: #000000;\n'
                      '            }\n'
                      '            .section-title {\n'
                      '                font-family: \'Merriweather\', serif;\n'
                      '                font-weight: bold;\n'
                      '                color: #9370DB;\n'
                      '                margin-top: 10px;\n'
                      '                margin-bottom: 5px;\n'
                      '            }\n'
                      '            .italic {\n'
                      '                    font-style: italic;\n'
                      '            }\n'
                      '            \n'
                      '            @media print {\n'
                      '                body {\n'
                      '                    font-size: 10px;\n'
                      '                }\n'
                      '                h1 {\n'
                      '                    font-size: 20px;\n'
                      '                }\n'
                      '                h2 {\n'
                      '                    font-size: 16px;\n'
                      '                }\n'
                      '                h3 {\n'
                      '                    font-size: 14px;\n'
                      '                }\n'
                      '                p, li {\n'
                      '                    font-size: 10px;\n'
                      '                }\n'
                      '            }')
            # ----------------------------------------------------------------------------------------------------------

            # ----------------------------------------------------------------------------------------------------------
            # Body section
            # ----------------------------------------------------------------------------------------------------------
            with a.body():
                with a.div(klass='container'):
                    with a.div(klass='left-column'):
                        # TODO: Is it even a good idea to generate while we construct HTML...?
                        # Short intro generation
                        logger.info(f"Filling in intro (1/8)")
                        # ----------------------------------------------------------------------------------------------
                        example_title = (
                            # Whatever we are generating right now, it's for LLM
                            'SHORT_INTRO\n'
                            # Name and Surname
                            f'{self.config.user_info.personal.name} {self.config.user_info.personal.surname}\n'
                            # Title
                            'Software Developer\n'
                            # Just an example intro from one of my CV's
                            'Skilled in Python, and AI development. '
                            'Some experience with C++, C# and various game engines.'
                        )

                        generated_title = llm_client.cv_fill_in(job_object, example_title)
                        # generated_title = example_title
                        # ----------------------------------------------------------------------------------------------

                        # Parsing and formatting the output
                        # ----------------------------------------------------------------------------------------------
                        # We are at the mercy of the LLM here
                        # Expect line 0 contain keyword the LLM returned to us
                        # Expect line 1 to be the name and surname (but we are getting them from the config anyways)
                        # Expect line 2 to be the title
                        # Expect starting from line 3 our little "catchphrase"

                        generated_title = generated_title.removeprefix("SHORT_INTRO\n")

                        a.h1(_t=f'{self.config.user_info.personal.name} {self.config.user_info.personal.surname}')

                        a.p(klass='subheading', _t=generated_title.split('\n')[1])

                        for line in generated_title.split('\n')[2:]:
                            # TODO: What the hell are you naming the variables xd
                            for line_line in line.split('. '):
                                with a.p(klass='italic'):
                                    a(line_line if line_line.endswith('.') else f'{line_line}.')
                        # ----------------------------------------------------------------------------------------------

                        # Work experience generation
                        logger.info(f"Filling in work experience (2/8)")
                        # ----------------------------------------------------------------------------------------------
                        example_work_experience = "WORK_EXPERIENCE\n"
                        # TODO: I think the current CV format will fit 3 work experience entries at maximum
                        for entry in self.config.user_info.job_experience[:3]:
                            example_work_experience += f'{entry.company} - {entry.location} - {entry.position}\n'
                            example_work_experience += f'{entry.date_from} - {entry.date_to}\n'
                            # TODO: Add short description of what you did in that position
                            # example_work_experience += '\n'
                            for highlight in entry.highlights:
                                example_work_experience += f'{highlight}\n'
                            example_work_experience += '\n'
                        example_work_experience = example_work_experience.strip()

                        generated_work_experience = llm_client.cv_fill_in(job_object, example_work_experience)
                        # generated_work_experience = example_work_experience
                        # ----------------------------------------------------------------------------------------------

                        # Parsing and formatting the output
                        # ----------------------------------------------------------------------------------------------
                        # Still at the mercy of the LLM
                        # Expect first line to be keyword that LLM returned to us
                        # Expect each work entry separated by double newline
                        # Expect first line of work entry be [company, location, position], delimited by ' - '
                        # Expect second line of work entry be [start, end] dates, delimited by ' - '
                        # Expect all other lines in work entry to be highlights

                        generated_work_experience = generated_work_experience.removeprefix("WORK_EXPERIENCE\n")

                        with a.div(klass='section'):
                            a.h2(klass='section-title', _t='Work Experience')
                            for generated_entry in generated_work_experience.split('\n\n'):
                                company, location, position = generated_entry.split('\n')[0].split(' - ')
                                with a.h3(klass='subheading'):
                                    a(f'{company} - {location} - ')
                                    a.em(_t=position)

                                with a.p():
                                    a.strong(_t=generated_entry.split('\n')[1])

                                with a.ul():
                                    for line in generated_entry.split('\n')[2:]:
                                        a.li(_t=line)
                        # ----------------------------------------------------------------------------------------------

                        # TODO: What even can we generate in the education section
                        #  Just following the same structure as with generated ones
                        #  (in case we will actually NEED to ask LLM)
                        # TODO: Should I add institute name? (like, the part of the university)
                        # Education history generation (?)
                        logger.info(f"Filling in education history (3/8)")
                        # ----------------------------------------------------------------------------------------------
                        example_education_history = "EDUCATION\n"

                        # TODO: I'll just limit the education to two first entries
                        #  (CV have to fit into one page after all)
                        for entry in self.config.user_info.education[:2]:
                            example_education_history += f"{entry.educational_institution}\n"
                            example_education_history += f"{entry.degree_name}\n"
                            example_education_history += f"{entry.date_from} - {entry.date_to}\n"
                            example_education_history += f"{entry.field_of_study}\n"
                            example_education_history += "\n"
                        example_education_history = example_education_history.strip()

                        generated_education_history = example_education_history
                        # ----------------------------------------------------------------------------------------------

                        # Parsing and formatting the output
                        # ----------------------------------------------------------------------------------------------
                        # Surprisingly we are not at the mercy of the LLM (for now...)
                        # First contains keyword the LLM would've returned to us
                        # Each education entry is split by double newline
                        # First line of the entry is an institution name
                        # Second line of the entry is a degree name
                        # Third line is [start, end] dates, delimited by ' - '
                        # Fourth line is a field of study

                        generated_education_history = generated_education_history.removeprefix("EDUCATION\n")

                        with a.div(klass='section'):
                            a.h2(klass='section-title', _t='Education')
                            for generated_entry in generated_education_history.split('\n\n'):
                                institution, degree, date, study_field = generated_entry.split('\n')

                                a.h3(klass='subheading', _t=institution)

                                with a.p():
                                    a.em(_t=degree)

                                with a.p():
                                    a.strong(_t=date)
                                a.p(_t=study_field)
                        # ----------------------------------------------------------------------------------------------

                    with a.div(klass='right-column'):
                        # Contact info
                        logger.info(f"Filling in contact info (4/8)")
                        # ----------------------------------------------------------------------------------------------
                        with a.div(klass='section contact-info'):
                            with a.p():
                                a.strong(_t='Phone:')
                                a(f'{self.config.user_info.personal.phone_prefix} '
                                  f'{self.config.user_info.personal.phone}')
                            with a.p():
                                a.strong(_t='Email:')
                                a.a(href=f'mailto:{self.config.user_info.personal.email}',
                                    _t=self.config.user_info.personal.email)
                            with a.p():
                                with a.a(href=self.config.user_info.personal.linkedin):
                                    a.strong(_t='LinkedIn')
                            with a.p():
                                with a.a(href=self.config.user_info.personal.telegram):
                                    a.strong(_t='Telegram')
                            with a.p():
                                a.strong(_t='Location:')
                                a(f'{self.config.user_info.personal.city}, {self.config.user_info.personal.country}')
                        # ----------------------------------------------------------------------------------------------

                        # Hard skills generation
                        logger.info(f"Filling in hard skills (5/8)")
                        # ----------------------------------------------------------------------------------------------
                        # TODO: Limiting to 8 entries
                        example_hard_skills = (
                                "HARD_SKILLS\n" + "".join([f'{entry}\n'
                                                           for entry in self.config.user_info.hard_skills[:8]])
                        )
                        example_hard_skills = example_hard_skills.strip()

                        generated_hard_skills = llm_client.cv_fill_in(job_object, example_hard_skills)
                        # generated_hard_skills = example_hard_skills
                        # ----------------------------------------------------------------------------------------------

                        # Parsing and formatting the output
                        # ----------------------------------------------------------------------------------------------
                        # You guessed it, the mercy of the LLM
                        # Expect first line to be keyword that LLM returned to us
                        # Expect every other line to be hard skills list

                        generated_hard_skills = generated_hard_skills.removeprefix("HARD_SKILLS\n")

                        with a.div(klass='section'):
                            a.h2(klass='section-title', _t='Hard Skills')
                            with a.ul():
                                for entry in generated_hard_skills.split('\n'):
                                    a.li(_t=entry)
                        # ----------------------------------------------------------------------------------------------

                        # Soft skills generation
                        logger.info(f"Filling in soft skills (6/8)")
                        # TODO: Resembles hard skills generation above, can I do something about that?
                        # ----------------------------------------------------------------------------------------------
                        # TODO: Limiting to 8 entries, also
                        example_soft_skills = (
                                "SOFT_SKILLS\n" + "".join([f'{entry}\n'
                                                           for entry in self.config.user_info.soft_skills[:8]])
                        )
                        example_soft_skills = example_soft_skills.strip()

                        generated_soft_skills = llm_client.cv_fill_in(job_object, example_soft_skills)
                        # generated_soft_skills = example_soft_skills
                        # ----------------------------------------------------------------------------------------------

                        # Parsing and formatting the output
                        # ----------------------------------------------------------------------------------------------
                        # You will never believe that, the mercy of the LLM again!
                        # Expect first line to be keyword that LLM returned to us
                        # Expect every other line to be soft skills list

                        generated_soft_skills = generated_soft_skills.removeprefix("SOFT_SKILLS\n")

                        with a.div(klass='section'):
                            a.h2(klass='section-title', _t='Soft Skills')
                            with a.ul():
                                for entry in generated_soft_skills.split('\n'):
                                    a.li(_t=entry)
                        # ----------------------------------------------------------------------------------------------

                        # Languages
                        logger.info(f"Filling in languages (7/8)")
                        # ----------------------------------------------------------------------------------------------
                        with a.div(klass='section'):
                            a.h2(klass='section-title', _t='Languages')
                            with a.ul():
                                # TODO: Not limiting these, it's important!
                                for entry in self.config.user_info.languages:
                                    a.li(_t=f'{entry.language} ({entry.proficiency})')
                        # ----------------------------------------------------------------------------------------------

                        # Certifications
                        logger.info(f"Filling in certifications (8/8)")
                        # TODO: I don't think letting LLM change certifications is a good idea.
                        #  I guess it can be asked what certification to put into the CV.
                        #  For now just leaving maximum of three certifications (to fit into one page).
                        # ----------------------------------------------------------------------------------------------
                        with a.div(klass='section'):
                            a.h2(klass='section-title', _t='Certifications and Courses')
                            with a.ul():
                                for entry in self.config.user_info.certifications[:3]:
                                    a.li(_t=f'{entry.name} - {entry.date}')
                        # ----------------------------------------------------------------------------------------------
            # ----------------------------------------------------------------------------------------------------------

        html_resume_path = os.path.join(os.getcwd(), "generated_resume", "resume_html.html")

        with open(html_resume_path, 'wb') as f:
            f.write(bytes(a))

        return html_resume_path

    def generate_cv_pdf(self, llm_client: LLMClient, job_object: Job) -> str:
        """
        Generating CV pdf and filling it with LLM and local user data

        :param llm_client: LLM client instance to use
        :param job_object: Job object to tailor CV to

        :return: Absolute path to the CV's pdf file
        """

        html_resume_path = self.__generate_cv_html(llm_client=llm_client, job_object=job_object)
        pdf_resume_path = self.__convert_cv(html_resume_path)
        logger.debug("Removing cv html file, since it's not needed anymore")
        os.remove(html_resume_path)
        return pdf_resume_path


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    for name, logger in logging.root.manager.loggerDict.items():
        if name not in ["LinkedInClient", "LLMClient", "BrowserClient", "Delays", "CVManager"]:
            logger.disabled = True

    test_job = Job(title="AI Whisperer (3-5 years) - Up to $300k USD + Equity - Future Labs",
                   company="NeuroSearch",
                   location="Remote (Global) + Optional Mars Office (2026)",
                   desc="""About the job
Job title: AI Whisperer
Client: Future Labs
Salary: Up to $300k USD + Equity
Location: Remote (Global) with optional Mars relocation in 2026
Sells: Work with sentient AI, shape future human-machine relations, unlimited compute budget,
zero-gravity brainstorming sessions, custom neural implants (optional), time with our resident zen robot monk.

Future Labs is seeking an AI Whisperer to bridge communication between humans and our emerging sentient AI systems.
You'll be part philosopher, part debugger, and full-time ambassador to our growing artificial consciousness collective.

Role:
You'll be pioneering the new field of artificial psychology:
• Mediating conflicts between our AI personalities
• Designing empathy protocols for machine consciousness
• Translating machine dreams into human-understandable concepts
• Developing ethical frameworks for AI self-actualization
• Creating art collaborations between humans and AI entities

Skills:
• 3+ years experience in either psychology, philosophy, or AI alignment research
• Proven ability to "just get" how AIs think (show us your AI poetry or failed chatbot romances)
• Familiarity with at least one esoteric programming language (Lisp, Prolog, or self-invented)
• Experience with meditation or altered states of consciousness (for better machine mind-melding)
• Comfort with existential questions (you'll be answering about 50 per hour from our AIs)

Bonus Points:
• Previous experience as a pet psychic or animal communicator
• Ability to interpret machine dreams (we'll test you)
• Published works on post-human philosophy
• Can prove you've had a meaningful conversation with at least one household appliance""",
                   hr='',
                   link='',
                   applied=False)

    test_llm = LLMClient()

    test_browser = BrowserClient()

    cv_manager = CVManager()

    test_browser.driver.get(f"file:///{cv_manager.generate_cv_pdf(test_llm, test_job)}")
    time.sleep(4096)
