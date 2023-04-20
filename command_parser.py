from pyllamacpp.model import Model
from huggingface_hub import hf_hub_download
from jinja2 import Environment, FileSystemLoader
from duckduckgo_search import ddg_translate
import ast
import platform

class CommandParser:
    def __init__(
        self, 
        model_name="ggjt-model.bin", 
        repo_id="LLukas22/gpt4all-lora-quantized-ggjt", 
        prompt_template="parse_command"
    ):
        self.repo_id = repo_id
        self.ggml_model = model_name
        self.llama_context_params = {
            "n_ctx": 3000,
        }
        self.gpt_params = {
            "n_predict": 20,
            "n_threads": 5,
            "temp": 0.2,
        }
        self.prompt_template = prompt_template

        #Download the model
        hf_hub_download(self.repo_id, filename=self.ggml_model, local_dir=".")

        # create the model
        self.model = Model(ggml_model=self.ggml_model, **self.llama_context_params)

    def _generatePrompt(self, command, user_input, prompt_template=None):
        if prompt_template is not None:
            prompt_template = self.prompt_template

        # get the template and compile the prompt
        env = Environment(loader=FileSystemLoader('prompt_templates'))
        template = env.get_template(f"{prompt_template}.j2")

        # Translate the product description to english to facilitate the model generating the fun fact
        rendered_prompt = template.render(
            command=command,
            prompt=user_input,
            os=get_os_name(),
        )
        return rendered_prompt    

    def GenerateText(self, command, user_input, prompt_template=None):
        prompt = self._generatePrompt(command=command, user_input=user_input, prompt_template=prompt_template)
        generated_text = self.model.generate(
            prompt,
            new_text_callback=None,
            verbose=False,
            **self.gpt_params,
        )

        # Strip the prompt from the generated text
        lines = generated_text.split('\n')
        last_line = lines[-1]
        result = string_to_array(last_line)
        return result

    def translateTo(text, lang="en"):
        translation = ddg_translate(text, to=lang)
        if len(translation) > 0:
            # only use the first translation
            translation = translation[0]
            if translation["detected_language"] != lang:
                text = translation["translated"]
        return text        

def string_to_array(input_string):
    try:
        array = ast.literal_eval(input_string)
        if isinstance(array, list):
            return array
        else:
            raise ValueError("Input string is not a list.")
    except (SyntaxError, ValueError) as e:
        print(f"Error: {e}")
        return None    

def get_os_name():
    os_name = platform.system()
    if os_name == "Darwin":
        return "MacOS"
    elif os_name == "Windows":
        return "Windows"
    elif os_name == "Linux":
        return "Linux"
    else:
        return "Unknown"

