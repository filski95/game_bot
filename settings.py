class Settings:
    def __init__(
        self,
        name,
        num_spell_cast,
        key_to_safety,
        last_key_anti_afk,
        anti_afk_frequency,
        run_fishing,
        fishing_break,
        run_for,
        fishing_cords,
    ) -> None:
        self.name = name
        self.num_spell_cast = num_spell_cast
        self.key_to_safety = key_to_safety
        self.last_key_anti_afk = last_key_anti_afk
        self.anti_afk_frequency = anti_afk_frequency
        self.run_fishing = run_fishing
        self.fishin_break = fishing_break
        self.run_for = run_for
        self.fishing_cords = fishing_cords
