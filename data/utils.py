import discord
import re


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
        for i in inputs:
            inp = i if i is not None else 'None'
            string += f'Inputs: {inp} '
        string += '.\n'
    if args:
        string += f'Args: {args}.\n'
    print(string)
# endregion
