from enum import Enum
from typing import List, Dict


class PetMood(Enum):
    """Enum representing different mood states of the pet."""

    ECSTATIC = "ecstatic"
    HAPPY = "happy"
    CONTENT = "content"
    SAD = "sad"
    WORRIED = "worried"


class Pet:
    """Represents the Grit Guardian pet that reflects user's habit performance."""

    def __init__(self, name: str = "Guardian", species: str = "Dragon"):
        """Initializes a new pet.

        Args:
            name: The pet's name (default: "Guardian")
            species: The pet's species (default: "Dragon")
        """
        self.name = name
        self.species = species
        self.current_mood = PetMood.CONTENT

    def calculate_mood(self, habits_data: List[Dict]) -> PetMood:
        """Calculates mood based on habit completion data.

        Args:
            habits_data: List of dictionaries containing habit analytics
                        Each dict should have 'completion_rate' and 'current_streak' keys

        Returns:
            PetMood enum value representing the calculated mood
        """
        if not habits_data:
            self.current_mood = PetMood.WORRIED
            return PetMood.WORRIED

        # Calculate average completion rate and streak status
        avg_completion = sum(h["completion_rate"] for h in habits_data) / len(
            habits_data
        )
        active_streaks = sum(1 for h in habits_data if h["current_streak"] > 0)
        streak_percentage = active_streaks / len(habits_data) if habits_data else 0

        # Update current mood based on performance
        if avg_completion >= 90 and streak_percentage == 1.0:
            self.current_mood = PetMood.ECSTATIC
        elif avg_completion >= 70:
            self.current_mood = PetMood.HAPPY
        elif avg_completion >= 50:
            self.current_mood = PetMood.CONTENT
        elif avg_completion >= 30:
            self.current_mood = PetMood.SAD
        else:
            self.current_mood = PetMood.WORRIED

        return self.current_mood

    # The following "artworks" are AI-generated for now
    # and will be updated in the future
    def get_ascii_art(self) -> str:
        """Returns ASCII art based on current mood.

        Returns:
            String containing ASCII art representation of the pet
        """
        art = {
            PetMood.ECSTATIC: r"""
    /\   /\
   (  O O  )
  <  \___/  >
   \   ^   /
    \_/_\_/""",
            PetMood.HAPPY: r"""
    /\   /\
   (  ^.^  )
  <  \___/  >
   \  ~~~  /""",
            PetMood.CONTENT: r"""
    /\   /\
   (  -.-  )
  <  \___/  >
   \  ---  /""",
            PetMood.SAD: r"""
    /\   /\
   (  -..-  )
  <  \___/  >
   \  vvv  /""",
            PetMood.WORRIED: r"""
    /\   /\
   (  o.o  )
  <  \___/  >
   \  ~~~  /""",
        }

        return art.get(self.current_mood, art[PetMood.CONTENT])

    def get_mood_message(self) -> str:
        """Gets a message based on the pet's current mood.

        Returns:
            String with a mood-appropriate message
        """
        messages = {
            PetMood.ECSTATIC: f"{self.name} is absolutely thrilled with your consistency!",
            PetMood.HAPPY: f"{self.name} is happy to see your progress!",
            PetMood.CONTENT: f"{self.name} is content with your efforts.",
            PetMood.SAD: f"{self.name} looks a bit sad. Some habits need attention.",
            PetMood.WORRIED: f"{self.name} is worried about your habits. Time to get back on track!",
        }

        return messages.get(
            self.current_mood, f"{self.name} is feeling {self.current_mood.value}."
        )

    def __str__(self) -> str:
        """String representation of the pet."""
        return f"{self.species} named {self.name} (Mood: {self.current_mood.value})"
