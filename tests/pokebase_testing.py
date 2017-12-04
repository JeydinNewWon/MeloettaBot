import pokebase as pb


#pokemon = pokebase.pokemon('rockruff')
'''
inaff = pokebase.api.make_obj(pokebase.api.lookup_data('move', 'sunny-day')).effect_entries[0].get('short_effect')

inaff = inaff.replace('\n', '')
inaff = inaff.replace('    ', ' ')
inaff = inaff.replace('   ', ' ')


print(inaff)
'''

'''
def get_eng(li, to_pass):
    for entry in li:
        if entry['language'].get('name') == 'en':
            return entry[to_pass]

inaff = pokebase.api.make_obj(pokebase.api.lookup_data('pokemon-species', 'rockruff')).evolution_chain.chain.evolves_to[0].get('species')['name']

print(inaff)
'''
move_d = pb.api.make_obj(pb.api.lookup_data('pokemon-species', 'lycanroc')).varieties[0].get('pokemon')['name']

print(move_d)


'''
my_string = 'M.spam Porky shrek is'

my_string = my_string.lower().split(' ')[1:]

key, value = my_string[0], '-'.join(my_string[1:])

print(key)
print(value)
'''