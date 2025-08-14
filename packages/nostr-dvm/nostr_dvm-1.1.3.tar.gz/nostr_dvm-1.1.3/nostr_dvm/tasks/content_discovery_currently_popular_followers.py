import json
from datetime import timedelta

from nostr_sdk import Timestamp, PublicKey, Tag, Keys, Options, SecretKey, NostrSigner, NostrDatabase, \
    ClientBuilder, Filter, SyncOptions, SyncDirection, init_logger, LogLevel, Event, Kind, \
    RelayLimits

from nostr_dvm.interfaces.dvmtaskinterface import DVMTaskInterface, process_venv
from nostr_dvm.utils import definitions
from nostr_dvm.utils.admin_utils import AdminConfig
from nostr_dvm.utils.definitions import EventDefinitions, relay_timeout
from nostr_dvm.utils.dvmconfig import DVMConfig, build_default_config
from nostr_dvm.utils.nip88_utils import NIP88Config, check_and_set_d_tag_nip88, check_and_set_tiereventid_nip88
from nostr_dvm.utils.nip89_utils import NIP89Config, check_and_set_d_tag, create_amount_tag
from nostr_dvm.utils.output_utils import post_process_list_to_events

"""
This File contains a Module to discover popular notes
Accepted Inputs: none
Outputs: A list of events 
Params:  None
"""


class DicoverContentCurrentlyPopularFollowers(DVMTaskInterface):
    KIND: Kind = EventDefinitions.KIND_NIP90_CONTENT_DISCOVERY
    TASK: str = "discover-content"
    FIX_COST: float = 0
    dvm_config: DVMConfig
    last_schedule: int
    db_since = 2 * 3600
    db_name = "db/nostr_recent_notes2.db"
    min_reactions = 2

    async def init_dvm(self, name, dvm_config: DVMConfig, nip89config: NIP89Config, nip88config: NIP88Config = None,
                       admin_config: AdminConfig = None, options=None):

        self.last_schedule = Timestamp.now().as_secs()

        if self.options.get("db_name"):
            self.db_name = self.options.get("db_name")
        if self.options.get("db_since"):
            self.db_since = int(self.options.get("db_since"))

        use_logger = False
        if use_logger:
            init_logger(LogLevel.DEBUG)

        if self.dvm_config.UPDATE_DATABASE:
            await self.sync_db()

    async def is_input_supported(self, tags, client=None, dvm_config=None):
        for tag in tags:
            if tag.as_vec()[0] == 'i':
                input_value = tag.as_vec()[1]
                input_type = tag.as_vec()[2]
                if input_type != "text":
                    return False
        return True

    async def create_request_from_nostr_event(self, event: Event, client=None, dvm_config=None):
        self.dvm_config = dvm_config

        request_form = {"jobID": event.id().to_hex()}

        # default values
        user = event.author().to_hex()
        max_results = 100

        for tag in event.tags().to_vec():
            if tag.as_vec()[0] == 'i':
                input_type = tag.as_vec()[2]
            elif tag.as_vec()[0] == 'param':
                param = tag.as_vec()[1]
                if param == "max_results":  # check for param type
                    max_results = int(tag.as_vec()[2])
                elif param == "user":  # check for param type
                    user = tag.as_vec()[2]

        options = {
            "max_results": max_results,
            "user": user,
        }
        request_form['options'] = json.dumps(options)
        return request_form

    async def process(self, request_form):
        from nostr_sdk import Filter
        from types import SimpleNamespace
        ns = SimpleNamespace()

        options = self.set_options(request_form)
        relaylimits = RelayLimits.disable()
        opts = (
            Options().relay_limits(
                relaylimits))
        sk = SecretKey.parse(self.dvm_config.PRIVATE_KEY)
        keys = Keys.parse(sk.to_hex())

        database = NostrDatabase.lmdb(self.db_name)
        cli = ClientBuilder().database(database).signer(NostrSigner.keys(keys)).opts(opts).build()
        for relay in self.dvm_config.SYNC_DB_RELAY_LIST:
            await cli.add_relay(relay)

        # ropts = RelayOptions().ping(False)
        # cli.add_relay_with_opts("wss://nostr.band", ropts)

        await cli.connect()

        user = PublicKey.parse(options["user"])
        followers_filter = Filter().author(user).kinds([Kind(3)])
        followers = await cli.fetch_events(followers_filter, relay_timeout)
        # print(followers)

        # Negentropy reconciliation
        # Query events from database
        timestamp_since = Timestamp.now().as_secs() - self.db_since
        since = Timestamp.from_secs(timestamp_since)

        result_list = []

        if len(followers.to_vec()) > 0:
            newest = 0
            best_entry = followers.to_vec()[0]
            for entry in followers.to_vec():
                if entry.created_at().as_secs() > newest:
                    newest = entry.created_at().as_secs()
                    best_entry = entry

            # print(best_entry.as_json())
            followings = []
            for tag in best_entry.tags().to_vec():
                if tag.as_vec()[0] == "p":
                    following = PublicKey.parse(tag.as_vec()[1])
                    followings.append(following)

            filter1 = Filter().kind(definitions.EventDefinitions.KIND_NOTE).authors(followings).since(since)
            events = await cli.database().query(filter1)
            if self.dvm_config.LOGLEVEL.value >= LogLevel.DEBUG.value:
                print("[" + self.dvm_config.NIP89.NAME + "] Considering " + str(len(events.to_vec())) + " Events")

            ns.finallist = {}
            for event in events.to_vec():
                # if event.created_at().as_secs() > timestamp_since:
                filt = Filter().kinds(
                    [definitions.EventDefinitions.KIND_ZAP, definitions.EventDefinitions.KIND_REACTION,
                     definitions.EventDefinitions.KIND_REPOST,
                     definitions.EventDefinitions.KIND_NOTE]).event(event.id()).since(since)
                reactions = await cli.database().query(filt)
                if len(reactions.to_vec()) >= self.min_reactions:
                    ns.finallist[event.id().to_hex()] = len(reactions.to_vec())

            finallist_sorted = sorted(ns.finallist.items(), key=lambda x: x[1], reverse=True)[
                               :int(options["max_results"])]
            for entry in finallist_sorted:
                # print(EventId.parse(entry[0]).to_bech32() + "/" + EventId.parse(entry[0]).to_hex() + ": " + str(entry[1]))
                e_tag = Tag.parse(["e", entry[0]])
                result_list.append(e_tag.as_vec())
            # await cli.connect()
            await cli.shutdown()
            if self.dvm_config.LOGLEVEL.value >= LogLevel.DEBUG.value:
                print("[" + self.dvm_config.NIP89.NAME + "] Filtered " + str(
                    len(result_list)) + " fitting events.")

        return json.dumps(result_list)

    async def post_process(self, result, event):
        """Overwrite the interface function to return a social client readable format, if requested"""
        for tag in event.tags().to_vec():
            if tag.as_vec()[0] == 'output':
                format = tag.as_vec()[1]
                if format == "text/plain":  # check for output type
                    result = post_process_list_to_events(result)

        # if not text/plain, don't post-process
        return result

    async def schedule(self, dvm_config):
        if dvm_config.SCHEDULE_UPDATES_SECONDS == 0:
            return 0
        # We simply use the db from the other dvm that contains all notes

        else:
            if Timestamp.now().as_secs() >= self.last_schedule + dvm_config.SCHEDULE_UPDATES_SECONDS:
                if self.dvm_config.UPDATE_DATABASE:
                    await self.sync_db()
                self.last_schedule = Timestamp.now().as_secs()
                return 1

    async def sync_db(self):
        try:
            sk = SecretKey.parse(self.dvm_config.PRIVATE_KEY)
            keys = Keys.parse(sk.to_hex())
            database = NostrDatabase.lmdb(self.db_name)
            cli = ClientBuilder().signer(NostrSigner.keys(keys)).database(database).build()

            for relay in self.dvm_config.SYNC_DB_RELAY_LIST:
                await cli.add_relay(relay)

            await cli.connect()

            timestamp_since = Timestamp.now().as_secs() - self.db_since
            since = Timestamp.from_secs(timestamp_since)

            filter1 = Filter().kinds(
                [definitions.EventDefinitions.KIND_NOTE, definitions.EventDefinitions.KIND_REACTION,
                 definitions.EventDefinitions.KIND_ZAP]).since(since)  # Notes, reactions, zaps

            # filter = Filter().author(keys.public_key())
            if self.dvm_config.LOGLEVEL.value >= LogLevel.DEBUG.value:
                print("[" + self.dvm_config.NIP89.NAME + "] Syncing notes of the last " + str(
                    self.db_since) + " seconds.. this might take a while..")
            dbopts = SyncOptions().direction(SyncDirection.DOWN)
            await cli.sync(filter1, dbopts)
            await cli.database().delete(Filter().until(Timestamp.from_secs(
                Timestamp.now().as_secs() - self.db_since)))  # Clear old events so db doesn't get too full.
            await cli.shutdown()
            if self.dvm_config.LOGLEVEL.value >= LogLevel.DEBUG.value:
                print("[" + self.dvm_config.NIP89.NAME + "] Done Syncing Notes of the last " + str(
                    self.db_since) + " seconds..")
        except Exception as e:
            print(e)


# We build an example here that we can call by either calling this file directly from the main directory,
# or by adding it to our playground. You can call the example and adjust it to your needs or redefine it in the
# playground or elsewhere
def build_example(name, identifier, admin_config, options, cost=0, update_rate=300, processing_msg=None,
                  update_db=True):
    dvm_config = build_default_config(identifier)
    dvm_config.USE_OWN_VENV = False
    dvm_config.SHOWLOG = True
    dvm_config.SCHEDULE_UPDATES_SECONDS = update_rate  # Every x seconds
    dvm_config.UPDATE_DATABASE = update_db
    # Activate these to use a subscription based model instead
    # dvm_config.SUBSCRIPTION_REQUIRED = True
    # dvm_config.SUBSCRIPTION_DAILY_COST = 1
    dvm_config.FIX_COST = cost
    dvm_config.CUSTOM_PROCESSING_MESSAGE = processing_msg
    admin_config.LUD16 = dvm_config.LN_ADDRESS

    image = "https://image.nostr.build/d92652a6a07677e051d647dcf9f0f59e265299b3335a939d008183a911513f4a.jpg"
    # Add NIP89
    nip89info = {
        "name": name,
        "picture": image,
        "about": "I show notes that are currently popular from people you follow",
        "lud16": dvm_config.LN_ADDRESS,
        "supportsEncryption": True,
        "acceptsNutZaps": dvm_config.ENABLE_NUTZAP,
        "personalized": True,
        "amount": create_amount_tag(cost),
        "nip90Params": {
            "max_results": {
                "required": False,
                "values": [],
                "description": "The number of maximum results to return (default currently 100)"
            }
        }
    }

    nip89config = NIP89Config()
    nip89config.DTAG = check_and_set_d_tag(identifier, name, dvm_config.PRIVATE_KEY, nip89info["picture"])
    nip89config.CONTENT = json.dumps(nip89info)

    # admin_config.UPDATE_PROFILE = False
    # admin_config.REBROADCAST_NIP89 = False

    return DicoverContentCurrentlyPopularFollowers(name=name, dvm_config=dvm_config, nip89config=nip89config,
                                                   options=options,
                                                   admin_config=admin_config)


def build_example_subscription(name, identifier, admin_config, options, processing_msg=None, update_db=True):
    dvm_config = build_default_config(identifier)
    dvm_config.USE_OWN_VENV = False
    dvm_config.SHOWLOG = True
    dvm_config.SCHEDULE_UPDATES_SECONDS = 180  # Every 3 minutes
    dvm_config.UPDATE_DATABASE = update_db
    # Activate these to use a subscription based model instead
    # dvm_config.SUBSCRIPTION_DAILY_COST = 1
    dvm_config.FIX_COST = 0
    dvm_config.CUSTOM_PROCESSING_MESSAGE = processing_msg

    # Add NIP89
    image = "https://image.nostr.build/d92652a6a07677e051d647dcf9f0f59e265299b3335a939d008183a911513f4a.jpg"
    nip89info = {
        "name": name,
        "picture": image,
        "about": "I show notes that are currently popular, just like the free DVM, I'm also used for testing subscriptions. (beta)",
        "lud16": dvm_config.LN_ADDRESS,
        "supportsEncryption": True,
        "acceptsNutZaps": dvm_config.ENABLE_NUTZAP,
        "personalized": True,
        "subscription": True,
        "nip90Params": {
            "max_results": {
                "required": False,
                "values": [],
                "description": "The number of maximum results to return (default currently 100)"
            }
        }
    }

    nip89config = NIP89Config()
    nip89config.DTAG = check_and_set_d_tag(identifier, name, dvm_config.PRIVATE_KEY, nip89info["picture"])
    nip89config.CONTENT = json.dumps(nip89info)

    nip88config = NIP88Config()
    nip88config.DTAG = check_and_set_d_tag_nip88(identifier, name, dvm_config.PRIVATE_KEY, nip89info["picture"])
    nip88config.TIER_EVENT = check_and_set_tiereventid_nip88(identifier, "1")
    nip89config.NAME = name
    nip88config.IMAGE = nip89info["picture"]
    nip88config.TITLE = name
    nip88config.AMOUNT_DAILY = 100
    nip88config.AMOUNT_MONTHLY = 2000
    nip88config.CONTENT = "Subscribe to the DVM for unlimited use during your subscription"
    nip88config.PERK1DESC = "Unlimited requests"
    nip88config.PERK2DESC = "Support NostrDVM & NostrSDK development"
    nip88config.PAYMENT_VERIFIER_PUBKEY = "5b5c045ecdf66fb540bdf2049fe0ef7f1a566fa427a4fe50d400a011b65a3a7e"

    # admin_config.FETCH_NIP88 = True
    # admin_config.EVENTID = "63a791cdc7bf78c14031616963105fce5793f532bb231687665b14fb6d805fdb"
    # admin_config.PRIVKEY = dvm_config.PRIVATE_KEY

    return DicoverContentCurrentlyPopularFollowers(name=name, dvm_config=dvm_config, nip89config=nip89config,
                                                   nip88config=nip88config, options=options,
                                                   admin_config=admin_config)


if __name__ == '__main__':
    process_venv(DicoverContentCurrentlyPopularFollowers)
