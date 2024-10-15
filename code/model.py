import base64
import pickle
import os
import json
import random
from ast import literal_eval
from io import BytesIO

import imagehash
from bs4 import BeautifulSoup
from PIL import Image

class Icon:
    def __init__(self, image_path: str, manual: str, context: str):
        self.image = Image.open(image_path)
        self.dhash = imagehash.dhash(self.image)
        self.image_type = "PNG"
        self.manual = manual
        self.context = context
        self.descriptions = {}
        self.meanings = {}
    
    def update_descriptions(self, new_desc: dict[str, str]):
        self.descriptions.update(new_desc)
    
    def update_meanings(self, new_meanings: dict[str, str]):
        self.meanings.update(new_meanings)

    def update_context(self, new_ctx: str):
        self.context = new_ctx

    def __str__(self):
        return f"Icon(dhash='{self.dhash}', manual='{self.manual}', context='{self.context}', descriptions='{self.descriptions}', meanings='{self.meanings}')"
    
    @property
    def imageb64(self):
        buff = BytesIO()
        self.image.save(buff, format=self.image_type)
        return base64.b64encode(buff.getvalue()).decode("utf-8")
    
    def save_image(self, filename: str):
        self.image.save(filename)


class Dataset():
    def __init__(self, name):
        self.name = name
        self._icons: dict[imagehash.ImageHash, Icon] = {}
    
    def load_manual(self, manual_name, html_file, img_folder, parser="html.parser", root_tag_name="", root_tag_attr={}, img_tag_name="img", img_tag_attr="src", ascend=2, max_context=100):
        page_content = self._get_content(html_file, parser, root_tag_name, root_tag_attr)
        for img in page_content.find_all(img_tag_name):
            img_filename = os.path.basename(img[img_tag_attr].strip())
            parent = img
            for _ in range(ascend):
                parent = parent.parent
            all_words = [word for s in parent.stripped_strings for word in s.split(" ")]
            context = " ".join(all_words[:max_context])
            i = Icon(f"{img_folder}/{img_filename}", manual_name, context)
            self._icons.update({i.dhash: i})

    def load_json(self, json_file):
        with open(json_file, "r") as infile:
            json_data = json.load(infile)
        for d in json_data:
            dhash = imagehash.hex_to_hash(d.get("id"))
            img_file = d.get("image_file")
            img_folder = os.path.dirname(json_file)
            img_path = f"{img_folder}/icons/{img_file}"
            manual = d.get("manual")
            context = d.get("context")
            desc = d.get("visual_descriptions")
            meaning = d.get("functional_descriptions")
            icon = self._icons.get(dhash)
            if not icon:
                icon = Icon(img_path, manual, context)
                icon.dhash = dhash
                self._icons.update({icon.dhash: icon})
            icon.update_descriptions(desc)
            icon.update_meanings(meaning)
    
    def save_html(self, html_file):
        with open(html_file, "w", encoding="utf-8") as outfile:
            outfile.write(self.as_html())
    
    def save_json(self, json_file):
        image_folder = f"{os.path.dirname(json_file)}/icons"
        if not os.path.isdir(image_folder):
            os.mkdir(image_folder)
        json_obj = []
        for icon in self.icons:
            icon.save_image(f"{image_folder}/{icon.dhash}.png")
            sample = {
                "id" : str(icon.dhash),
                "image_file" : f"{icon.dhash}.png",
                "manual": icon.manual,
                "context": icon.context,
                "visual_descriptions" : icon.descriptions,
                "functional_descriptions" : icon.meanings
            }
            json_obj.append(sample)
        with open(json_file, "w", encoding="utf-8") as outfile:
            json.dump(json_obj, outfile, ensure_ascii=False, indent=4)

    @property
    def icons(self):
        return list(self._icons.values())
    
    def delete_icon(self, dhash: str):
        self._icons.pop(imagehash.hex_to_hash(dhash))

    def split_train_test(self, n):
        all_icons = self.icons[:]
        random.shuffle(all_icons)
        train = Dataset(f"{self.name} - Train")
        test = Dataset(f"{self.name} - Test")
        train._icons = {i.dhash : i for i in all_icons[:n]}
        test._icons = {i.dhash : i for i in all_icons[n:]}
        return train, test

    def as_html(self):
        html = f"""<!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <title>{self.name}</title>
        <style>
            table {{border: 1px solid #ddd;}}
            th, td {{border: 1px solid #ddd;}}
        </style>
        </head>
        <body>
        <table>
        <tr><th>dHash</th><th>Image</th><th>Manual</th><th>Context</th><th>Description</th><th>Meaning</th></tr>"""
        for img in self.icons:
            row = (
                f"<tr><td>{img.dhash}</td>"
                f'<td><img src="data:image/{img.image_type};base64,{img.imageb64}" width="100"></td>'
                f"<td>{img.manual}</td>"
                f"<td>{img.context}</td>"
                f"<td>{img.descriptions}</td>"
                f"<td>{img.meanings}</td></tr>"
            )
            html += row
        html+= "</table>\n</body>\n</html>"
        return html

    def _get_content(self, html_file, parser, root_tag_name="", root_tag_attr={}):
        with open(html_file) as fp:
            soup = BeautifulSoup(fp, parser)        
        if root_tag_name:
            return soup.find(name=root_tag_name)
        if root_tag_attr:
            return soup.find(attrs=root_tag_attr)  
        return soup  
