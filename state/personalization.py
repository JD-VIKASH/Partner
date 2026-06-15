class PersonalizationLayer:
    def format_prompt_modifier(self, profile: dict) -> str:
        """Generates dynamic instructions based on user profile."""
        style = profile.get("speaking_style_preference", "calm")
        return f"Adjust your tone to match a {style} style. Be proactive in offering help related to their active interests."
