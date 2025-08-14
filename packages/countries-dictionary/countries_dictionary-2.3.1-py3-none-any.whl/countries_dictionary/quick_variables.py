"""Some prepared functions which might or might not be helpful"""

from countries_dictionary import COUNTRIES
from countries_dictionary.russia import RUSSIA
from countries_dictionary.vietnam import VIETNAM
import json

def chosen_dictionary(dictionary="countries"):
    """Returns one of the dictionaries depends on the parameter. Used in other functions"""
    if dictionary.casefold() == "countries": return COUNTRIES
    elif dictionary.casefold() == "russia": return RUSSIA
    elif dictionary.casefold() == "vietnam": return VIETNAM
    else: raise Exception("This dictionary does not exist (yet)")

def json_dictionary(indent: int | str | None = None, dictionary="countries"):
    """Converts the chosen dictionary into a JSON string"""
    x = chosen_dictionary(dictionary)
    return json.dumps(x, indent=indent)

def sorted_dictionary(chosen_key: str, reverse: bool = True, dictionary="countries"):
    """Sorts the chosen dictionary by a sortable key"""
    x = chosen_dictionary(dictionary)
    return dict(sorted(x.items(), key=lambda item: item[1][chosen_key], reverse=reverse))

def filtered_dictionary(chosen_key: str, chosen_value: int | str, dictionary="countries"):
    """Filters the chosen dictionary by a key"""
    x = chosen_dictionary(dictionary)
    if chosen_key == "continents" or chosen_key == "official languages":
        return dict(filter(lambda item: chosen_value in item[1][chosen_key], x.items()))
    else: return dict(filter(lambda item: item[1][chosen_key] == chosen_value, x.items()))
    # This is still under development

def countries_population_density():
    """Returns the countries dictionary with the `population density` key included in the countries' keys
    - Population density (in people per square kilometre) = Population / Land area"""
    new_countries = COUNTRIES
    for x in COUNTRIES: new_countries[x]["population density"] = COUNTRIES[x]["population"] / COUNTRIES[x]["land area"]
    return new_countries

def russia_population_density():
    """Returns the Russia dictionary with the `population density` key included in the countries' keys
    - Population density (in people per square kilometre) = Population / Land area"""
    new_russia = RUSSIA
    for x in RUSSIA: new_russia[x]["population density"] = RUSSIA[x]["population"] / RUSSIA[x]["area"]
    return new_russia

def vietnam_population_density():
    """Returns the Vietnam dictionary with the `population density` key included in the countries' keys
    - Population density (in people per square kilometre) = Population / Area"""
    new_vietnam = VIETNAM
    for x in VIETNAM: new_vietnam[x]["population density"] = VIETNAM[x]["population"] / VIETNAM[x]["area"]
    return new_vietnam

def countries_population_density():
    """Returns the countries dictionary with the `GDP per capita` key included in the countries' keys
    - GDP per capita (in dollars per person) = Nominal GDP / Population"""
    new_countries = COUNTRIES
    for x in COUNTRIES: new_countries[x]["GDP per capita"] = COUNTRIES[x]["nominal GDP"] / COUNTRIES[x]["population"]
    return new_countries

def countries_france_censored():
    """Returns the countries dictionary with the `France` key gets censored `Fr*nce`
    (This is only a joke, I don't support hate against France and French people)"""
    new_countries = COUNTRIES
    new_countries["Fr*nce"] = new_countries.pop("France")
    new_countries = dict(sorted(new_countries.items()))
    return new_countries