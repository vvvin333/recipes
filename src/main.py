import json
from math import inf
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel

app = FastAPI(debug=True)

DATA_PATH = "data/recipes.json"


class Item(BaseModel):
    name: str
    q: int


class RecommendedRecipe(BaseModel):
    name: str
    q: int


@app.get("/")
async def root():
    return parse_recipes_dict(DATA_PATH)


def ingredients_dict(ingredients: dict[str, list[str | int]]) -> dict[str, int]:
    result = {}
    for name, q in zip(ingredients["name"], ingredients["q"]):
        result[name] = q
    return result


def parse_recipes_dict(filename: str) -> dict[str, dict[str, int]]:
    result = {}
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
    return result
