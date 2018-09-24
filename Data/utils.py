import discord
import re
from discord.ext import commands
from typing import List, Optional, Tuple, Union


def clean_html(string: str) \
        -> str:
    if string is None:
        return ''
    string = string.replace('<br><br>', '\n\n\t')
    string = string.replace('<br>', '\n\t')
    string = re.sub('<[a-zA-Z#= /\'0-9]*>', '**', string)
    return string


def clean_string(string: str) \
        -> str:
    if string is None:
        return ''
    return string.strip().replace(' ', '').upper()


def create_embed_template(description: str, color: int, requester: Optional[str]=None, thumbnail: Optional[str]=None,
                          image: Optional[str]=None, author: Optional[str]=None, author_url: Optional[str]=None,
                          icon_url: Optional[str]=None) \
        -> discord.Embed:
    embed = discord.Embed(colour=color, description=description)
    if requester is not None:
        embed.set_footer(text=f'Requested by @{requester}.')
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    if image is not None:
        embed.set_image(url=image)
    if author is not None:
        if author_url is None:
            author_url = ''
        if icon_url is None:
            icon_url = ''
        embed.set_author(name=author, icon_url=icon_url, url=author_url)
    return embed


async def display_embed(ctx: commands.Context, content: Optional[str]=None,
                        embeds: Optional[List[discord.Embed]]=None) \
        -> None:
    for i, e in enumerate(embeds):
        if i == 0:
            await ctx.send(content=content, embed=e)
        else:
            await ctx.send(embed=e)


def generate_blocks(items: Union[List, str], block_size: int) \
        -> Union[List, str]:
    return [items[i:i + block_size] for i in range(0, len(items), block_size)]


def parse_arguments(args: str, prefix: str) \
        -> Optional[List[str]]:
    try:
        if prefix == '\\':
            prefix += '\\'
        return re.split(f' ?{prefix}', args)
    except TypeError:
        raise commands.UserInputError
    except ValueError:
        raise commands.UserInputError


def parse_single_argument(args: List[str], valid_args: List[str], prefix: str, val_prefix: str, has_value: bool=False) \
        -> Tuple[bool, Optional[str]]:
    if args is None:
        return False, None
    value = None
    found = False
    valid_args = [a.upper() for a in valid_args]
    for a in args:
        try:
            if val_prefix == '\\':
                val_prefix += '\\'
            if prefix == '\\':
                prefix += '\\'
            split = re.split(val_prefix, a)
            split = [s.replace(f'{prefix}', '') for s in split]
        except ValueError:
            raise commands.UserInputError
        if split[0] in valid_args:
            found = True
            if has_value and len(split) > 1:
                value = split[1]
                break
    return found, value


def parse_many_value_argument(values: str, valid_values: List[str], delimiter: str) \
        -> Optional[List[str]]:
    if values is None:
        return None
    try:
        split = re.split(delimiter, values)
        split = [clean_string(s) for s in split]
    except ValueError:
        raise commands.UserInputError

    for s in split:
        if s not in valid_values:
            raise commands.UserInputError
    return split


def print_command(command: str, inputs: Optional[List]=None, args: Optional[str]=None) \
        -> None:
    display_string = f'Invoked: {command}.\n'
    if inputs is not None:
        display_string += 'Inputs: '
        for i in inputs:
            display_string += f'{[i if i is not None else "None"]}'
        display_string += '.\n'
    if args is not None:
        display_string += f'Args: {args}.\n'
    print(display_string)
