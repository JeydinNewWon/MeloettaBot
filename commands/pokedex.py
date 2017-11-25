import discord
from discord.ext import commands
from utils import config as c
import pokebase as pb

config = c.Config
fail = config.fail
success = config.success


class PokeDex(object):
    def __init__(self, bot):
        self.bot = bot

    def to_pb_object(self, void):
        return pb.api.make_obj(void)

    async def get_pokemon_info(self, pokemon):
        pokemon_d = None
        try:
            pokemon_d = pb.api.lookup_data('pokemon', pokemon)
            pokemon_d = self.to_pb_object(pokemon_d)
        except:
            await self.bot.say('{} Invalid pokemon name.'.format(fail))

        stats = pokemon_d.stats
        abilities = pokemon_d.abilities
        pokemon_pic = pokemon_d.sprites.front_default
        dex_id = str(pokemon_d.id)
        types = pokemon_d.types

        stats.reverse()
        abilities.reverse()
        types.reverse()

        return [stats, abilities, pokemon_pic, dex_id, types]

    @commands.command(pass_context=True)
    async def pokedex(self, ctx, pokemon):
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
            ability_list.append(ability_name)

        abilities = ' '.join(ability_list)

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


def setup(bot):
    bot.add_cog(PokeDex(bot))