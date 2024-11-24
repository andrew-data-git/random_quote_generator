import requests
import json
from PIL import Image, ImageFont, ImageDraw, ImageChops, ImageFilter
from pathlib import Path
import os
from textwrap import TextWrapper


def get_quote(mode: str = 'random', options: list = []):
    '''Provide the response JSON from ZenQuotes'''
    api_url = f'https://zenquotes.io?api={mode}'
    api_options = ''
    if len(options) > 0:
        for i,option in enumerate(options):
            api_options.append(f'option{i+1}&{option}&')
        api_options[:-1] # remove redundant ampersand
    response = requests.get(api_url+api_options)

    if response.status_code == requests.codes.ok:
        return response.json()[0] # parse to json and unlist
    else:
        print("Error:", response.status_code, response.text)
        return None

def parse_quote_response(response: json):
    '''Extract quote and author from JSON'''
    quote = response['q']
    author = response['a']
    return quote, author

def get_image():
    '''Provide the response JSON from LoremPicsum'''
    api_url = f'https://picsum.photos/400/400'
    response = requests.get(api_url)
    if response.status_code == 200:
        # Save the image locally
        with open("image.png", "wb") as file:
            file.write(response.content)
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")

def dodge(base, blend):
    '''Apply dodge to an image'''
    base = base.convert("L")
    blend = blend.convert("L")
    result = ImageChops.dodge(base, blend)
    return result

def create_inspiration(base_image: Image, quote: str, author: str):
    '''Draw the quote onto the image, and save'''
    image_dimensions = base_image.size
    white, glow, trans = (255,255,255), (65,15,100,255), (0,0,0,0) # colours

    # Format text
    wrapper = TextWrapper(width = 25,# image_dimensions[0],
                          break_long_words=True)
    wrapped_quote = '\n'.join(wrapper.wrap(quote))
    wrapped_author = '\n'.join(wrapper.wrap(author))
    wrapped_text = wrapped_quote+'\n'+' - '+wrapped_author.upper()

    # Parameters
    font = ImageFont.truetype("cmtt10.ttf", 25)
    pos = (5,image_dimensions[0]//4)

    # Manipulate base image
    base_image = base_image.filter(ImageFilter.BLUR)

    # Add a new layer for holding the glow and paste
    glow_layer = Image.new("RGBA", image_dimensions, trans)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=15))
    draw = ImageDraw.Draw(glow_layer)
    draw.text(pos, wrapped_text, font=font, fill=glow)
    base_image.paste(glow_layer, (0, 0), glow_layer)

    # Create another transparent layer for the text
    text_layer = Image.new("RGBA", base_image.size, trans)
    draw = ImageDraw.Draw(text_layer)
    draw.text(pos, wrapped_text, font=font, fill=white)
    base_image.paste(text_layer, (0, 0), text_layer)

    # Return
    base_image.save('inspiration.png')

#######################################################

if __name__ == '__main__':
    # Make quote
    quote = get_quote()
    quote, author = parse_quote_response(response=quote)

    # Make image
    get_image()
    image = Image.open(Path('image.png'))
    os.remove(Path('image.png'))

    # Create and save inspiration
    create_inspiration(image, quote, author)
    print('Inspo saved as "inspiration.png"')