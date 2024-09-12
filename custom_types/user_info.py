from dataclasses import dataclass
from utils import PrettyPrintable


@dataclass
class UserInfo(PrettyPrintable):
    personal: "Personal" = None
    education: list["Education"] = None
    job_experience: list["JobExperience"] = None
    hard_skills: list = None
    soft_skills: list = None
    projects: list["Project"] = None
    achievements: list["Achievement"] = None
    certifications: list["Certification"] = None
    languages: list["Language"] = None
    interests: list = None
    availability: str = ""
    expected_salary_range_usd: str = None
    self_identification: "SelfIdentification" = None
    legal_authorization: "LegalAuthorization" = None
    work_preferences: "WorkPreferences" = None

    @staticmethod
    def from_user_info_yaml(user_info_yaml):
        """
        Construct UserInfo instance from user_info.yaml

        :param user_info_yaml: loaded yaml object from user_info.yaml
        :return: UserInfo instance with provided data
        """
        # DIRTIEST piece of Python code ever, any inspection engine would scream its lungs off xd
        # It can fail spectacularly, but for now it works

        # Basically what these lines do: wrapping dicts from yaml object with actual dataclasses
        user_info = UserInfo(**user_info_yaml.copy())
        user_info.personal = Personal(**user_info.personal.copy())  # noqa
        user_info.education = [Education(**ed) for ed in user_info.education.copy()]  # noqa
        for ed in user_info.education:
            if ed.exams is not None:
                ed.exams = [Exam(**ex) for ex in ed.exams.copy()]  # noqa
        # hard_skills already a list of strings
        # soft_skills already a list of strings
        user_info.projects = [Project(**p) for p in user_info.projects.copy()]  # noqa
        user_info.achievements = [Achievement(**a) for a in user_info.achievements.copy()]  # noqa
        user_info.certifications = [Certification(**c) for c in user_info.certifications.copy()]  # noqa
        user_info.languages = [Language(**la) for la in user_info.languages.copy()]  # noqa
        # interests already a list of strings
        # availability already a string
        # expected_salary_range_us already a string
        user_info.self_identification = SelfIdentification(**user_info.self_identification.copy())  # noqa
        user_info.legal_authorization = LegalAuthorization(**user_info.legal_authorization.copy())  # noqa
        user_info.work_preferences = WorkPreferences(**user_info.work_preferences.copy())  # noqa
        return user_info


@dataclass
class Personal(PrettyPrintable):
    name: str = None
    surname: str = None
    birthday: str = None
    country: str = None
    city: str = None
    address: str = None
    phone_prefix: str = None
    phone: str = None
    email: str = None
    github: str = None
    linkedin: str = None
    telegram: str = None


@dataclass
class Education(PrettyPrintable):
    degree_name: str = None
    educational_institution: str = None
    field_of_study: str = None
    date_from: str = None
    date_to: str = None
    gpa: str = None
    exams: list["Exam"] = None


@dataclass
class Exam(PrettyPrintable):
    name: str = None
    score: str = None


@dataclass
class JobExperience(PrettyPrintable):
    position: str = None
    company: str = None
    location: str = None
    industry: str = None
    date_from: str = None
    date_to: str = None
    highlights: list[str] = None


@dataclass
class Project(PrettyPrintable):
    name: str = None
    description: str = None
    link: str = None


@dataclass
class Achievement(PrettyPrintable):
    name: str = None
    date: str = None
    description: str = None


@dataclass
class Certification(PrettyPrintable):
    name: str = None
    date: str = None


@dataclass
class Language(PrettyPrintable):
    language: str = None
    proficiency: str = None


@dataclass
class SelfIdentification(PrettyPrintable):
    gender: str = None
    pronouns: str = None
    veteran: str = None
    disability: str = None
    ethnicity: str = None


@dataclass
class LegalAuthorization(PrettyPrintable):
    eu_work_authorization: bool = None
    us_work_authorization: bool = None
    requires_us_visa: bool = None
    requires_us_sponsorship: bool = None
    requires_eu_visa: bool = None
    legally_allowed_to_work_in_eu: bool = None
    legally_allowed_to_work_in_us: bool = None
    requires_eu_sponsorship: bool = None


@dataclass
class WorkPreferences(PrettyPrintable):
    remote_work: bool = None
    in_person_work: bool = None
    open_to_relocation: bool = None
    willing_to_complete_assessments: bool = None
    willing_to_undergo_drug_tests: bool = None
    willing_to_undergo_background_checks: bool = None
