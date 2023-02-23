import json


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
