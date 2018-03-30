import discord
import re
from typing import Any, Callable, List, Optional, Tuple, Union


# region Utility Methods
def create_embed_template(description: str, color: int, requester: str=None, thumbnail: str=None, image: str=None,
                          author: str=None, author_url: str=None, icon_url: str=None) -> discord.Embed:
    embed = discord.Embed(colour=color, description=description)
    if requester is not None:
        embed.set_footer(text=f'Requested by @{requester}.')
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    if image is not None:
        embed.set_image(url=image)
    if author is not None:
        if author_url is None:
            if icon_url is None:
                embed.set_author(name=author)
            else:
                embed.set_author(name=author, icon_url=icon_url)
        else:
            if icon_url is None:
                embed.set_author(name=author, url=author_url)
            else:
                embed.set_author(name=author, url=author_url, icon_url=icon_url)
    return embed


def get_sanitized_value(value: str) -> str:
    splits = re.split('_', value)
    splits = [x.capitalize() for x in splits]
    return ' '.join(splits)


def print_command(command: str, inputs: list=None, args: str=None) -> None:
    string = 'Invoked: {}.\n'.format(command)
    if inputs:
        string += 'Inputs: '
        for i in inputs:
            inp = i if i is not None else 'None'
            string += f'{inp} '
        string += '.\n'
    if args:
        string += f'Args: {args}.\n'
    print(string)


def add_to_embed(current_embed: discord.Embed, split: int, embeds_list: List[discord.Embed], item_list: List[Any],
                 field_name_gen: Callable[[int, Any], str], field_value_gen: Callable[[int, Any], str],
                 field_inline_gen: Callable[[int, Any], bool], embed_gen: Callable[[], discord.Embed]) \
        -> List[discord.Embed]:
    for i, o in enumerate(item_list):
        current_embed.add_field(name=field_name_gen(i, o), value=field_value_gen(i, o), inline=field_inline_gen(i, o))
        if i % split >= split - 1:
            embeds_list.append(current_embed)
            current_embed = embed_gen()
        elif len(item_list) - i == 1:
            embeds_list.append(current_embed)
    return embeds_list
# endregion
