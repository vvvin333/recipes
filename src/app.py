from datetime import datetime, timedelta
from math import inf
from http import HTTPStatus
from fastapi import FastAPI, Query

import app_logger
from constants import RECIPES_DIRECTORY_PATH, DATETIME_FORMAT
from models import RecommendedRecipe
from shortcuts import parse_recipes_dict, ingredients_dict, parse_logs

app = FastAPI(debug=True)
formatter = app_logger.CustomFormatter('%(asctime)s')
logger = app_logger.get_logger(__name__, formatter)


@app.get("/")
async def root():
    return parse_recipes_dict(RECIPES_DIRECTORY_PATH)


@app.get("/suggest_recipes/")
def get_recipes(
        name: list[str] = Query(default=...),
        q: list[int] = Query(default=...),
) -> list[RecommendedRecipe]:
    result: list[RecommendedRecipe] = []
    ingredients = ingredients_dict({"name": name, "q": q})

    recipes = parse_recipes_dict(RECIPES_DIRECTORY_PATH)
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
    logger.info(f"Recipes: {'; '.join(['%s'] * len(result))}", *result)

    return result


@app.get("/last_suggests/")
def get_last_suggested_recipes(
        hours: int = Query(default=...),
) -> list[str]:
    result = []
    for item in parse_logs():
        suggestion = item.get("recipes", {}).get("log", {})
        if "Recipes:" in suggestion.get("msg_template"):
            log_time = datetime.strptime(suggestion["timestamp"], DATETIME_FORMAT)
            start = datetime.now() - timedelta(hours=hours)
            if log_time >= start:
                result.append(suggestion["message"])
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        reload=True,
    )
