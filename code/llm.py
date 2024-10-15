from model import Icon, Dataset

from abc import ABC, abstractmethod
import json

import openai
import anthropic

class LLM(ABC):
    def __init__(self, client, model):
        self.client = client
        self.model = model
    
    def get_captions(self, train: Dataset, test: Dataset, k: int, instructions: str, prompt: str, treatment: str, max_tokens=500, use_image=True, use_context=True, rerun=False):
        icon: Icon
        for icon in test.icons:
            if (not rerun) or (treatment not in icon.descriptions) or (treatment not in icon.meanings):
                # k_shot = random.sample(train.icons, k)
                msgs = []
                k_shot = self._k_closest(icon, train.icons, k) if k > 0 else []
                for sample in k_shot:
                    p = self._make_prompt_msg(sample, prompt, use_image, use_context)
                    r = self._make_response_msg(
                        visual_content = sample.descriptions["ground-truth"], 
                        meaning = sample.meanings["ground-truth"] 
                    )
                    msgs.append(p)
                    msgs.append(r)
                msgs.append(self._make_prompt_msg(icon, prompt, use_image, use_context))
                description, meaning = self._get_caption(instructions, msgs, max_tokens)
                if description and meaning:
                    # print(icon.dhash, description, meaning) 
                    icon.descriptions[treatment] = description
                    icon.meanings[treatment] = meaning

    def _get_caption(self, instructions, msgs, max_tokens, retry_on_error=3):
        description, meaning = None, None
        for _ in range(retry_on_error):
            try:
                response = self._get_response(instructions, msgs, max_tokens)
                description, meaning = self._process_response(response)
            except openai.BadRequestError as e:
                print("BadRequestError:", e)
            except anthropic.InternalServerError as e:
                print("InternalServerError:", e)
            except OSError as e:
                print("OS error:", e)
            except KeyError as e:
                print("KeyError:", e)
            except ValueError as e:
                print("ValueError:", e)
            except Exception as e:
                raise
        return description, meaning

    def _k_closest(self, icon: Icon, icon_list: list[Icon], k: int):
        result = sorted(icon_list[:], key=lambda sample: sample.dhash - icon.dhash)
        return result[:k]
    
    def _process_response(self, json_str: str):
        json_obj = json.loads(json_str)
        description = json_obj['visual_content']
        meaning = json_obj['meaning']    
        return description, meaning
    
    @abstractmethod
    def _make_prompt_msg(self, icon: Icon, prompt: str, use_image: bool, use_context: bool):
        pass

    @abstractmethod
    def _make_response_msg(self, **kwargs):
        pass

    @abstractmethod
    def _get_response(self, instructions: str, messages: list, max_tokens: int):
        pass


class GPT(LLM):
    def _make_prompt_msg(self, icon: Icon, prompt: str, use_image: bool, use_context: bool):
        content = [{"type": "text", "text": f"{prompt} {icon.context}" if use_context else prompt}]        
        if use_image:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{icon.image_type};base64,{icon.imageb64}",
                    "detail": "auto"
                }
            })        
        return {"role": "user", "content": content}

    def _make_response_msg(self, **kwargs):
        result = {}
        for key, value in kwargs.items():
            result[key] = value
        return {"role": "assistant", "content": json.dumps(result)}

    def _get_response(self, instructions :str, messages: list, max_tokens: int):
        messages.insert(0, {"role": "system", "content": instructions})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=max_tokens
        )
        caption = ""
        if response.choices[0].finish_reason == "stop":
            caption = response.choices[0].message.content
        return caption
    
    def list_models(self):
        return [m for m in self.client.models.list()]


class Claude(LLM):
    def _make_prompt_msg(self, icon: Icon, prompt: str, use_image: bool, use_context: bool):
        content = [{"type": "text", "text": f"{prompt} {icon.context}" if use_context else prompt}]        
        if use_image:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{icon.image_type.lower()}",
                    "data": icon.imageb64
                }
            })        
        return {"role": "user", "content": content}

    def _make_response_msg(self, **kwargs):
        result = {}
        for key, value in kwargs.items():
            result[key] = value
        return {"role": "assistant", "content": json.dumps(result)}

    def _get_response(self, instructions :str, messages: list, max_tokens: int):
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            system=instructions,
            max_tokens=max_tokens
        )
        caption = ""
        if response.stop_reason == "end_turn":
            caption = response.content[0].text
        return caption


class Llava(LLM):
    def _make_prompt_msg(self, icon: Icon, prompt: str, use_image: bool, use_context: bool):
        content = f"{prompt} {icon.context}" if use_context else prompt
        image = [f"{icon.imageb64}"]     
        if use_image:
            return {"role": "user", "content": content, "images": image}    
        return {"role": "user", "content": content}

    def _make_response_msg(self, **kwargs):
        result = {}
        for key, value in kwargs.items():
            result[key] = value
        return {"role": "assistant", "content": json.dumps(result)}

    def _get_response(self, instructions :str, messages: list, max_tokens: int):
        messages.insert(0, {"role": "system", "content": instructions})
        response = self.client.chat(
            model = self.model, 
            messages = messages,
            format = "json",
            stream = False
        )
        caption = ""
        if response.get("done_reason") == "stop":
            caption = response.get("message").get("content")
        return caption
