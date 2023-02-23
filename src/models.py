from pydantic import BaseModel


class RecommendedRecipe(BaseModel):
    name: str
    q: int

    def __str__(self):
        return f"{self.name}: {self.q}"
