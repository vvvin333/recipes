from math import inf

from fastapi import Query

from main import app, DATA_PATH, logger
from models import RecommendedRecipe
from shortcuts import parse_recipes_dict, ingredients_dict


@app.get("/")
async def root():
    return parse_recipes_dict(DATA_PATH)


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
