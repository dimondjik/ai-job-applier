from dataclasses import dataclass


@dataclass
class FewShotPrompt:
    system_message: str = ""
    user_message_template: str = ""
    examples: list["OneShot"] = None

    @staticmethod
    def from_prompts_yaml(prompts_yaml):
        # Similar to same method in UserInfo
        prompts = FewShotPrompt(**prompts_yaml.copy())
        prompts.examples = [OneShot(**e) for e in prompts.examples]  # noqa
        return prompts


@dataclass
class OneShot:
    user_message: str = ""
    ai_message: str = ""
