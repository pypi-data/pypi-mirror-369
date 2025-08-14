import json
import os
import re

from nostr_sdk import Tag, Kind

from nostr_dvm.interfaces.dvmtaskinterface import DVMTaskInterface, process_venv
from nostr_dvm.utils.admin_utils import AdminConfig
from nostr_dvm.utils.definitions import EventDefinitions
from nostr_dvm.utils.dvmconfig import DVMConfig, build_default_config
from nostr_dvm.utils.nip88_utils import NIP88Config
from nostr_dvm.utils.nip89_utils import NIP89Config, check_and_set_d_tag
from nostr_dvm.utils.nostr_utils import get_referenced_event_by_id, get_events_by_ids, get_event_by_id

"""
This File contains a Module to generate Text, based on a prompt using the Unleashed.chat API.

Accepted Inputs: Prompt (text)
Outputs: Generated text
"""


class SummarizationUnleashedChat(DVMTaskInterface):
    KIND: Kind = EventDefinitions.KIND_NIP90_SUMMARIZE_TEXT
    TASK: str = "text-to-text"
    FIX_COST: float = 10
    dependencies = [("nostr-dvm", "nostr-dvm"),
                    ("openai", "openai")]

    async def init_dvm(self, name, dvm_config: DVMConfig, nip89config: NIP89Config, nip88config: NIP88Config = None,
                       admin_config: AdminConfig = None, options=None):
        dvm_config.SCRIPT = os.path.abspath(__file__)

    async def is_input_supported(self, tags, client=None, dvm_config=None):
        for tag in tags:
            if tag.as_vec()[0] == 'i':
                print(tag.as_vec())
                input_value = tag.as_vec()[1]
                input_type = tag.as_vec()[2]
                if input_type != "event" and input_type != "job" and input_type != "text":
                    return False

        return True

    async def create_request_from_nostr_event(self, event, client=None, dvm_config=None):
        request_form = {"jobID": event.id().to_hex() + "_" + self.NAME.replace(" ", "")}
        prompt = ""
        collect_events = []
        nostr_mode = True

        for tag in event.tags().to_vec():
            if tag.as_vec()[0] == 'i':
                input_type = tag.as_vec()[2]
                if input_type == "text":
                    prompt += tag.as_vec()[1] + "\n"
                elif input_type == "event":
                    collect_events.append(tag.as_vec()[1])
                    # evt = get_event_by_id(tag.as_vec()[1], client=client, config=dvm_config)
                    # prompt += evt.content() + "\n"
                elif input_type == "job":
                    evt = await get_referenced_event_by_id(event_id=tag.as_vec()[1], client=client,
                                                           kinds=[EventDefinitions.KIND_NIP90_RESULT_EXTRACT_TEXT,
                                                                  EventDefinitions.KIND_NIP90_RESULT_SUMMARIZE_TEXT,
                                                                  EventDefinitions.KIND_NIP90_RESULT_TRANSLATE_TEXT,
                                                                  EventDefinitions.KIND_NIP90_RESULT_CONTENT_DISCOVERY],
                                                           dvm_config=dvm_config)
                    if evt is None:
                        print("Event not found")
                        raise Exception

                    if evt.kind() == EventDefinitions.KIND_NIP90_RESULT_CONTENT_DISCOVERY:
                        result_list = json.loads(evt.content())
                        prompt = ""
                        for tag in result_list:
                            e_tag = Tag.parse(tag)
                            evt = await get_event_by_id(e_tag.as_vec()[1], client=client, config=dvm_config)
                            prompt += evt.content() + "\n"

                    else:
                        prompt = evt.content()

        evts = await get_events_by_ids(collect_events, client=client, config=dvm_config)
        if evts is not None:
            for evt in evts:
                prompt += evt.content() + "\n"

        clean_prompt = re.sub(r'^https?:\/\/.*[\r\n]*', '', prompt, flags=re.MULTILINE)
        options = {
            "prompt": clean_prompt[:4000],
            "nostr": nostr_mode,
        }
        request_form['options'] = json.dumps(options)

        return request_form

    async def process(self, request_form):
        from openai import OpenAI
        temp_open_ai_api_key = os.environ["OPENAI_API_KEY"]
        os.environ["OPENAI_API_KEY"] = os.getenv("UNLEASHED_API_KEY")
        options = self.set_options(request_form)

        try:
            client = OpenAI(
                base_url='https://unleashed.chat/api/v1',
            )

            print('Models:\n')

            for model in client.models.list():
                print('- ' + model.id)

            content = "Summarize the following notes: " + str(options["prompt"])
            normal_stream = client.chat.completions.create(
                messages=[
                    {
                        'role': 'user',
                        'content': content,
                    }
                ],
                model='dolphin-2.2.1-mistral-7b',
                stream=True,
                extra_body={
                    'nostr_mode': options["nostr"],
                },
            )

            print('\nChat response: ', end='')

            result = ""
            for chunk in normal_stream:
                result += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end='')

            os.environ["OPENAI_API_KEY"] = temp_open_ai_api_key
            return result

        except Exception as e:
            print("Error in Module: " + str(e))
            raise Exception(e)


# We build an example here that we can call by either calling this file directly from the main directory,
# or by adding it to our playground. You can call the example and adjust it to your needs or redefine it in the
# playground or elsewhere
def build_example(name, identifier, admin_config):
    dvm_config = build_default_config(identifier)
    dvm_config.SEND_FEEDBACK_EVENTS = True
    admin_config.LUD16 = dvm_config.LN_ADDRESS

    nip89info = {
        "name": name,
        "picture": "https://unleashed.chat/_app/immutable/assets/hero.pehsu4x_.jpeg",
        "about": "I summarize Text with https://unleashed.chat",
        "supportsEncryption": True,
        "acceptsNutZaps": False,
        "nip90Params": {}
    }

    nip89config = NIP89Config()
    nip89config.DTAG = check_and_set_d_tag(identifier, name, dvm_config.PRIVATE_KEY, nip89info["picture"])
    nip89config.CONTENT = json.dumps(nip89info)
    admin_config2 = AdminConfig()
    admin_config2.REBROADCAST_NIP89 = False

    return SummarizationUnleashedChat(name=name, dvm_config=dvm_config, nip89config=nip89config,
                                      admin_config=admin_config2)


if __name__ == '__main__':
    process_venv(SummarizationUnleashedChat)
