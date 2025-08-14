from nostr_sdk import Tag, Keys, EventBuilder, Kind

from nostr_dvm.utils.definitions import EventDefinitions
from nostr_dvm.utils.nostr_utils import send_event
from nostr_dvm.utils.print_utils import bcolors


async def announce_dm_relays(dvm_config, client):
    tags = []

    for relay in dvm_config.RELAY_LIST:
        r_tag = Tag.parse(["r", relay])
        tags.append(r_tag)

    keys = Keys.parse(dvm_config.NIP89.PK)
    content = ""

    event = EventBuilder(Kind(10050), content).tags(tags).sign_with_keys(keys)
    response_status = await send_event(event, client=client, dvm_config=dvm_config, broadcast=True)
    if response_status is not None:
        print(
            bcolors.BLUE + "[" + dvm_config.NIP89.NAME + "] Announced DM relays for " + dvm_config.NIP89.NAME + ". Success: " + str(
                response_status.success) + " Failed: " + str(response_status.failed) + " EventID: "
            + response_status.id.to_hex() + " / " + response_status.id.to_bech32())
    else:
        print(
            bcolors.RED + "[" + dvm_config.NIP89.NAME + "] Could not announce DM relays for " + dvm_config.NIP89.NAME + bcolors.ENDC)


async def nip65_announce_relays(dvm_config, client):
    # todo we might want to call the dm relays seperately but for now we do it together with the inbox relays
    await announce_dm_relays(dvm_config, client)

    tags = []

    for relay in dvm_config.RELAY_LIST:
        r_tag = Tag.parse(["r", relay])
        tags.append(r_tag)

    keys = Keys.parse(dvm_config.NIP89.PK)
    content = ""

    event = EventBuilder(EventDefinitions.KIND_RELAY_ANNOUNCEMENT, content).tags(tags).sign_with_keys(keys)
    response_status = await send_event(event, client=client, dvm_config=dvm_config, broadcast=True)
    if response_status is not None:
        print(
            bcolors.BLUE + "[" + dvm_config.NIP89.NAME + "] Announced NIP 65 for " + dvm_config.NIP89.NAME + ". Success: " + str(
                response_status.success) + " Failed: " + str(response_status.failed) + " EventID: "
            + response_status.id.to_hex() + " / " + response_status.id.to_bech32() + bcolors.ENDC)
    else:
        print(
            bcolors.RED + "[" + dvm_config.NIP89.NAME + "] Could not announce NIP 65 for " + dvm_config.NIP89.NAME + bcolors.ENDC)
