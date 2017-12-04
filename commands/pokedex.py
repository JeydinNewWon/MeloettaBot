import discord
from discord.ext import commands
from utils import config as c
import pokebase as pb

config = c.Config()
fail = config.fail
success = config.success


class PokeDex(object):
    def __init__(self, bot):
        self.bot = bot

    def to_pb_object(self, void):
        return pb.api.make_obj(void)

    def get_eng(self, li, to_pass):
        for entry in li:
            if entry['language'].get('name') == 'en':
                return entry[to_pass]

    async def get_item_info(self, item_name):
        item_d = None
        try:
            item_d = pb.api.lookup_data('item', item_name)
            item_d = self.to_pb_object(item_d)
        except:
            await self.bot.say('{} Invalid item name.'.format(fail))
            return

        names = item_d.names
        entries = item_d.effect_entries
        name = self.get_eng(names, 'name')
        descrip = self.get_eng(entries, 'effect')
        descrip = descrip.replace('\n', '')
        descrip = descrip.replace('    ', ' ')
        descrip = descrip.replace('   ', ' ')
        sprite = item_d.sprites.default

        return [name, descrip, sprite]

    async def get_move_info(self, move_name):
        move_d = None
        try:
            move_d = pb.api.lookup_data('move', move_name)
            move_d = self.to_pb_object(move_d)
        except:
            await self.bot.say('{} Invalid move name.'.format(fail))

        names = move_d.names
        name = self.get_eng(names, 'name')
        type = move_d.type.name.title()
        base_power = str(move_d.power)
        accuracy = str(move_d.accuracy) + '%'
        damage_type = move_d.damage_class.name.title()
        entries = move_d.effect_entries
        flavor_entries = move_d.flavor_text_entries
        descrip = self.get_eng(flavor_entries, 'flavor_text').replace('\n', ' ')
        effect = self.get_eng(entries, 'short_effect')

        return [name, type, base_power, accuracy, damage_type, descrip, effect]

    async def get_pokemon_info(self, pokemon_name):
        pokemon_d = None
        try:
            pokemon_d = pb.api.lookup_data('pokemon', pokemon_name)
            pokemon_d = self.to_pb_object(pokemon_d)
            pokemon_s = pokemon_d.species
        except:
            try:
                pokemon_s = pb.api.lookup_data('pokemon-species', pokemon_name)
                pokemon_s = self.to_pb_object(pokemon_s)
                pokemon_d = pokemon_s.varieties[0].get('pokemon')['name']
                pokemon_d = pb.api.lookup_data('pokemon', pokemon_d)
                pokemon_d = self.to_pb_object(pokemon_d)

            except:
                await self.bot.say('{} Invalid pokemon name.'.format(fail))
                return

        named = pokemon_d.name

        if pokemon_d.forms[0]:
            named = pokemon_d.forms[0].get('name')

        stats = pokemon_d.stats
        abilities = pokemon_d.abilities
        pokemon_pic = pokemon_d.sprites.front_default
        dex_id = str(pokemon_d.id)
        types = pokemon_d.types
        evolves_from = str(pokemon_s.evolves_from_species).title()
        evolves_to_chain = pokemon_s.evolution_chain.chain.evolves_to

        try:
            evolves_to_list = [i['species']['name'].lower() for i in evolves_to_chain[0].get('evolves_to')]
        except:
            evolves_to_list = None

        if evolves_to_list == []:
            evolves_to_list = [i.get('species')['name'].lower() for i in evolves_to_chain]

        new_evolves_to_list = []

        if evolves_to_list:
            for x in evolves_to_list:
                pokemon_evolve_s = pb.api.lookup_data('pokemon-species', x.lower())
                for name in pokemon_evolve_s.get('varieties'):
                    y = name['pokemon'].get('name').title()
                    if '-Mega' not in y:
                        new_evolves_to_list.append(y)

        if new_evolves_to_list == []:
            new_evolves_to_list = str(None)

        stats.reverse()
        abilities.reverse()
        types.reverse()

        return [stats, abilities, pokemon_pic, dex_id, types, evolves_from, new_evolves_to_list, named]


    '''
    @commands.command(pass_context=True)
    async def pokedex(self, ctx, pokemon):
        await self.bot.send_typing(ctx.message.channel)

        pokemon = pokemon.lower()
        pokemon_info = await self.get_pokemon_info(pokemon)
        embed = discord.Embed(
            colour=discord.Colour.green()
        )
        base_stats = [str(i.get('base_stat')) for i in pokemon_info[0]]
        abilities = pokemon_info[1]
        pokemon_pic = pokemon_info[2]
        dex_no = pokemon_info[3]
        types = ', '.join([x.get('type')['name'].title() for x in pokemon_info[4]])


        ability_list = []
        for ability in abilities:
            ability_name = ability.get('ability').get('name')
            if ability.get('is_hidden'):
                ability_name += ' **(Hidden)**'
            ability_list.append(ability_name.title())

        abilities = ', '.join(ability_list)

        embed.set_image(url=pokemon_pic)
        embed.add_field(name='HP', value=base_stats[0], inline=True)
        embed.add_field(name='Attack', value=base_stats[1], inline=True)
        embed.add_field(name='Defence', value=base_stats[2], inline=True)
        embed.add_field(name='Special Attack', value=base_stats[3], inline=True)
        embed.add_field(name='Special Defence', value=base_stats[4], inline=True)
        embed.add_field(name='Speed', value=base_stats[5], inline=True)
        embed.add_field(name='Types', value=types)
        embed.add_field(name='Abilities', value=abilities, inline=False)
        embed.set_footer(text='#{}'.format(dex_no))
        embed.set_author(name=pokemon.title())

        await self.bot.say(embed=embed)
    '''

    @commands.command(pass_context=True, no_pm=True)
    async def pokedex(self, ctx):
        message = ctx.message
        args = None
        try:
            args = message.content.lower().split(' ')[1:]
        except:
            await self.bot.say('{} No valid arguments given.'.format(fail))

        key, value = args[0], '-'.join(args[1:])

        if args[0] == 'item':
            await self.bot.send_typing(ctx.message.channel)
            item_info = None
            try:
                item_info = await self.get_item_info(value)
            except:
                self.bot.say('{} Invalid item name.'.format(fail))
                return

            name, descrip, sprite = item_info[0], item_info[1], item_info[2]

            embed = discord.Embed(
                colour=discord.Colour.green()
            )
            embed.set_author(name=name)
            embed.add_field(name='Description', value='*{}*'.format(descrip))
            embed.set_thumbnail(url=sprite)

            await self.bot.say(embed=embed)

        elif args[0] == 'move':
            await self.bot.send_typing(ctx.message.channel)
            move_info = None
            try:
                move_info = await self.get_move_info(value)
            except:
                self.bot.say('{} Invalid move name.'.format(fail))
                return

            name = move_info[0]
            type = move_info[1]
            base_power = move_info[2]
            accuracy = move_info[3]
            damage_type = move_info[4]
            descrip = move_info[5]
            effect = move_info[6]

            embed = discord.Embed(
                colour=discord.Colour.green()
            )

            embed.set_author(name=name)
            embed.add_field(name='Type', value=type, inline=False)
            embed.add_field(name='Category', value=damage_type, inline=False)
            embed.add_field(name='Base Power', value=base_power, inline=True)
            embed.add_field(name='Accuracy', value=accuracy, inline=True)
            embed.add_field(name='Description', value=descrip, inline=False)
            embed.add_field(name='Effect', value=effect, inline=False)

            await self.bot.say(embed=embed)

        else:
            await self.bot.send_typing(ctx.message.channel)

            pokemon_info = await self.get_pokemon_info(key)
            embed = discord.Embed(
                colour=discord.Colour.green()
            )
            name = pokemon_info[7].title()
            base_stats = [str(i.get('base_stat')) for i in pokemon_info[0]]
            abilities = pokemon_info[1]
            pokemon_pic = pokemon_info[2]
            dex_no = pokemon_info[3]
            types = ', '.join([x.get('type')['name'].title() for x in pokemon_info[4]])
            evolves_from = str(pokemon_info[5])
            evolves_into = pokemon_info[6]

            if evolves_into != 'None' and name not in evolves_into:
                evolves_into = ', '.join(evolves_into)
            else:
                evolves_into = 'None'

            ability_list = []
            for ability in abilities:
                ability_name = ability.get('ability').get('name')
                if ability.get('is_hidden'):
                    ability_name += ' **(Hidden)**'
                ability_list.append(ability_name.title())

            abilities = ', '.join(ability_list)

            embed.set_image(url=pokemon_pic)
            embed.add_field(name='Evolves from', value=evolves_from, inline=True)
            embed.add_field(name='Evolves into', value=evolves_into, inline=True)
            embed.add_field(name='HP', value=base_stats[0], inline=True)
            embed.add_field(name='Attack', value=base_stats[1], inline=True)
            embed.add_field(name='Defence', value=base_stats[2], inline=True)
            embed.add_field(name='Special Attack', value=base_stats[3], inline=True)
            embed.add_field(name='Special Defence', value=base_stats[4], inline=True)
            embed.add_field(name='Speed', value=base_stats[5], inline=True)
            embed.add_field(name='Types', value=types)
            embed.add_field(name='Abilities', value=abilities, inline=False)
            embed.set_footer(text='#{}'.format(dex_no))
            embed.set_author(name=name)

            await self.bot.say(embed=embed)

        return


def setup(bot):
    bot.add_cog(PokeDex(bot))