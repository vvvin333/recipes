import json
import logging

from fastapi import FastAPI, Query
from math import inf
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

DATA_PATH = "data/recipes.json"


class RecommendedRecipe(BaseModel):
    name: str
    q: int

    def __str__(self):
        return f"{self.name}: {self.q}"


@app.get("/")
async def root():
    return parse_recipes_dict(DATA_PATH)


def ingredients_dict(ingredients: dict[str, list[str | int]]) -> dict[str, int]:
    result = {}
    for name, q in zip(ingredients["name"], ingredients["q"]):
        result[name] = q
    return result


def parse_recipes_dict(filename: str) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    with (file := open(filename)):
        data = json.load(file)
        for recipe in data["recipes"]:
            result[recipe["name"]] = {}
            for item in recipe["components"]:
                result[recipe["name"]] |= {
                    item["item"]: item["q"]
                }
    return result


@app.get("/suggest_recipes/")
def get_recipes(
        name: list[str] = Query(default=...),
        q: list[int] = Query(default=...),
) -> list[RecommendedRecipe]:
    result: list[RecommendedRecipe] = []
    ingredients = ingredients_dict({"name": name, "q": q})

    recipes = parse_recipes_dict(DATA_PATH)
    if not recipes:
        logger.warning("No recipes")
        return []

    for recipe_name, recipe_ingredients in recipes.items():
        item = RecommendedRecipe(
            name=recipe_name,
            q=0,
        )
        min_max_for_recipe = inf
        for ingredient_name, ingredient_q in recipe_ingredients.items():
            max_portions = ingredients.get(ingredient_name, 0)//ingredient_q
            min_max_for_recipe = min(min_max_for_recipe, max_portions)
        item.q = min_max_for_recipe
        result.append(item)
    logger.info(f"Recipes were chosen: {'; '.join(['%s'] * len(result))}", *result)

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        reload=True,
    )
