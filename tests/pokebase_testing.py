import pokebase
import requests
import json




#pokemon = pokebase.pokemon('rockruff')
inaff = pokebase.api.make_obj(pokebase.api.lookup_data('pokemon', 'gardevoir'))
types = inaff.id


print(types)