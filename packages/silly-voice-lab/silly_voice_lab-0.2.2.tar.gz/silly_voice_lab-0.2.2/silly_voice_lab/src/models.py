from dataclasses import dataclass, field


@dataclass
class Character:
    name: str = "name"
    voice_id: str = "voice_id"
    gender: str = "m"

    def __post_init__(self) -> None:
        if self.gender not in ("m", "f"):
            raise ValueError("gender must be 'm' or 'f'")


@dataclass
class Group:
    group: str = ""
    characters: list[Character] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.characters)
    def __post_init__(self) -> None:
        if self.group is None:
            self.group = ""


@dataclass
class Configuration:
    input_folder: str = "scenario"
    output_folder: str = "voices"
    debug: bool = True
    converter: str = "dev"
    elevenlabs_api_key: str = "no_key"
    female_voice_id: str = "default"
    male_voice_id: str = "default"
