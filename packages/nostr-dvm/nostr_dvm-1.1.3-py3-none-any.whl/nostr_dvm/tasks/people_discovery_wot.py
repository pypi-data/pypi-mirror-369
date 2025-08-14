import csv
import csv
import json
import os
from datetime import timedelta

import networkx as nx
import pandas as pd
from nostr_sdk import Timestamp, PublicKey, Tag, Keys, Options, SecretKey, NostrSigner, NostrDatabase, \
    ClientBuilder, Filter, SyncOptions, SyncDirection, init_logger, LogLevel, Kind

from nostr_dvm.interfaces.dvmtaskinterface import DVMTaskInterface, process_venv
from nostr_dvm.utils.admin_utils import AdminConfig
from nostr_dvm.utils.definitions import EventDefinitions
from nostr_dvm.utils.dvmconfig import DVMConfig, build_default_config
from nostr_dvm.utils.nip88_utils import NIP88Config, check_and_set_d_tag_nip88, check_and_set_tiereventid_nip88
from nostr_dvm.utils.nip89_utils import NIP89Config, check_and_set_d_tag, create_amount_tag
from nostr_dvm.utils.output_utils import post_process_list_to_users

"""
This File contains a Module to discover users followed by users you follow, based on WOT
Accepted Inputs: none
Outputs: A list of users 
Params:  None
"""


class DiscoverPeopleWOT(DVMTaskInterface):
    KIND: Kind = EventDefinitions.KIND_NIP90_PEOPLE_DISCOVERY
    TASK: str = "discover-people"
    FIX_COST: float = 0
    dvm_config: DVMConfig
    request_form = None
    last_schedule: int
    db_since = 3600
    db_name = "db/nostr_followlists.db"
    personalized = True
    result = ""

    async def init_dvm(self, name, dvm_config: DVMConfig, nip89config: NIP89Config, nip88config: NIP88Config = None,
                       admin_config: AdminConfig = None, options=None):

        dvm_config.SCRIPT = os.path.abspath(__file__)
        self.request_form = {"jobID": "generic"}
        opts = {
            "max_results": 50,
        }
        self.request_form['options'] = json.dumps(opts)

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
        if not self.personalized:
            self.result = await self.calculate_result(self.request_form)

    async def is_input_supported(self, tags, client=None, dvm_config=None):
        for tag in tags:
            if tag.as_vec()[0] == 'i':
                input_value = tag.as_vec()[1]
                input_type = tag.as_vec()[2]
                if input_type != "text":
                    return False
        return True

    async def create_request_from_nostr_event(self, event, client=None, dvm_config=None):
        self.dvm_config = dvm_config

        request_form = {"jobID": event.id().to_hex()}

        # default values
        max_results = 50
        user = event.author().to_hex()
        print(user)
        hops = 2
        dunbar = 1000

        for tag in event.tags().to_vec():
            if tag.as_vec()[0] == 'i':
                input_type = tag.as_vec()[2]
            elif tag.as_vec()[0] == 'param':
                param = tag.as_vec()[1]
                if param == "max_results":  # check for param type
                    max_results = int(tag.as_vec()[2])
                elif param == "user":  # check for param type
                    user = tag.as_vec()[2]
                    print(user)
                elif param == "hops":  # check for param type
                    hops = int(tag.as_vec()[2])
                    print(hops)
                elif param == "dunbar":  # check for param type
                    dunbar = int(tag.as_vec()[2])
                    print(dunbar)

        options = {
            "user": user,
            "max_results": max_results,
            "hops": hops,
            "dunbar": dunbar,
        }
        request_form['options'] = json.dumps(options)
        return request_form

    async def process(self, request_form):
        # if the dvm supports individual results, recalculate it every time for the request
        if self.personalized:
            return await self.calculate_result(request_form)
        # else return the result that gets updated once every scheduled update. In this case on database update.
        else:
            return self.result

    async def calculate_hop(self, options, list_users, hop, dunbar):
        print("Fetching hop: " + str(hop))
        file = "db/" + options["user"] + ".csv"
        friendlist = []
        for friend in list_users:
            for npub in friend.friends:
                friendlist.append(npub)
        print(len(friendlist))
        user_friends_next_level = await analyse_users(friendlist, dunbar)
        write_to_csv(user_friends_next_level, file)
        return user_friends_next_level

    async def calculate_result(self, request_form):
        from types import SimpleNamespace
        ns = SimpleNamespace()

        options = self.set_options(request_form)
        file = "db/" + options["user"] + ".csv"
        try:
            print("Deleting existing file, creating new one")
            os.remove(file)
        except:
            print("Creating new file")
        # sync the database, this might take a while if it's empty or hasn't been updated in a long time

        # hop1
        user_id = PublicKey.parse(options["user"]).to_hex()

        user_friends_level1 = await analyse_users(
            [user_id])  # for the first user, ignore dunbar, thats the user after all.
        friendlist = []
        for npub in user_friends_level1[0].friends:
            friendlist.append(npub)
        levelusers = [Friend(user_id, friendlist)]
        write_to_csv(levelusers, file)

        for i in range(1, int(options["hops"])):
            levelusers = await self.calculate_hop(options, levelusers, i, int(options["dunbar"]))

        df = pd.read_csv(file, sep=',')
        df.info()
        df.tail()

        G_fb = nx.read_edgelist(file, delimiter=",", create_using=nx.DiGraph(), nodetype=str)
        print(G_fb)
        pr = nx.pagerank(G_fb)
        # Use this to find people your followers follow

        sorted_nodes = sorted([(node, pagerank) for node, pagerank in pr.items() if node not in friendlist],
                              key=lambda x: pr[x[0]],
                              reverse=True)[:int(options["max_results"])]
        for node in sorted_nodes:
            print(node[0] + "," + str(node[1]))

        result_list = []
        for entry in sorted_nodes:
            # print(EventId.parse(entry[0]).to_bech32() + "/" + EventId.parse(entry[0]).to_hex() + ": " + str(entry[1]))
            e_tag = Tag.parse(["p", entry[0], str(entry[1])])
            result_list.append(e_tag.as_vec())

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
                    result = post_process_list_to_users(result)

        # if not text/plain, don't post-process
        return result

    async def schedule(self, dvm_config):
        if dvm_config.SCHEDULE_UPDATES_SECONDS == 0:
            return 0
        else:
            if Timestamp.now().as_secs() >= self.last_schedule + dvm_config.SCHEDULE_UPDATES_SECONDS:
                if self.dvm_config.UPDATE_DATABASE:
                    await self.sync_db()
                self.last_schedule = Timestamp.now().as_secs()
                if not self.personalized:
                    self.result = await self.calculate_result(self.request_form)
                return 1

    async def sync_db(self):
        sk = SecretKey.parse(self.dvm_config.PRIVATE_KEY)
        keys = Keys.parse(sk.to_hex())
        database = NostrDatabase.lmdb(self.db_name)
        cli = ClientBuilder().signer(NostrSigner.keys(keys)).database(database).build()

        for relay in self.dvm_config.SYNC_DB_RELAY_LIST:
            await cli.add_relay(relay)

        await cli.connect()

        timestamp_since = Timestamp.now().as_secs() - self.db_since
        since = Timestamp.from_secs(timestamp_since)

        filter1 = Filter().kind(Kind(3))

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
            print(
                "[" + self.dvm_config.NIP89.NAME + "] Done Syncing Notes of the last " + str(
                    self.db_since) + " seconds..")


async def analyse_users(user_ids=None, dunbar=100000000):
    if user_ids is None:
        user_ids = []
    try:
        user_keys = []
        for npub in user_ids:
            try:
                user_keys.append(PublicKey.parse(npub))
            except Exception as e:
                print(npub)
                print(e)

        database = NostrDatabase.lmdb("db/nostr_followlists.db")
        followers_filter = Filter().authors(user_keys).kind(Kind(3))
        followers = await database.query(followers_filter)
        allfriends = []
        if len(followers.to_vec()) > 0:
            for follower in followers.to_vec():
                frens = []
                if len(follower.tags().to_vec()) < dunbar:
                    for tag in follower.tags().to_vec():
                        if tag.as_vec()[0] == "p":
                            frens.append(tag.as_vec()[1])
                    allfriends.append(Friend(follower.author().to_hex(), frens))
                else:
                    print("Skipping friend: " + follower.author().to_hex() + "Following: " + str(
                        len(follower.tags().to_vec())) + " npubs")

            return allfriends
        else:
            print("no followers")
            return []
    except Exception as e:
        print(e)
        return []


class Friend(object):
    def __init__(self, user_id, friends):
        self.user_id = user_id
        self.friends = friends


def write_to_csv(friends, file="friends222.csv"):
    with open(file, 'a') as f:
        writer = csv.writer(f)
        for friend in friends:
            for fren in friend.friends:
                row = [friend.user_id, fren]
                writer.writerow(row)


# We build an example here that we can call by either calling this file directly from the main directory,
# or by adding it to our playground. You can call the example and adjust it to your needs or redefine it in the
# playground or elsewhere
def build_example(name, identifier, admin_config, options, cost=0, update_rate=180, processing_msg=None,
                  update_db=True):
    dvm_config = build_default_config(identifier)
    dvm_config.USE_OWN_VENV = False
    dvm_config.SHOWLOG = True
    dvm_config.SCHEDULE_UPDATES_SECONDS = update_rate  # Every 10 minutes
    dvm_config.UPDATE_DATABASE = update_db
    # Activate these to use a subscription based model instead
    # dvm_config.SUBSCRIPTION_REQUIRED = True
    # dvm_config.SUBSCRIPTION_DAILY_COST = 1
    dvm_config.FIX_COST = cost
    dvm_config.CUSTOM_PROCESSING_MESSAGE = processing_msg
    admin_config.LUD16 = dvm_config.LN_ADDRESS

    image = "https://image.nostr.build/3cdd70113e05375e6240f2ecca5d9f4ee783ab386b00cc07ca907b601ab91a85.jpg",

    # Add NIP89
    nip89info = {
        "name": name,
        "picture": image,
        "about": "I show notes that are currently popular",
        "lud16": dvm_config.LN_ADDRESS,
        "supportsEncryption": True,
        "acceptsNutZaps": dvm_config.ENABLE_NUTZAP,
        "personalized": False,
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

    return DiscoverPeopleWOT(name=name, dvm_config=dvm_config, nip89config=nip89config,
                             admin_config=admin_config, options=options)


def build_example_subscription(name, identifier, admin_config, options, update_rate=180, processing_msg=None,
                               update_db=True):
    dvm_config = build_default_config(identifier)
    dvm_config.USE_OWN_VENV = False
    dvm_config.SHOWLOG = True
    dvm_config.SCHEDULE_UPDATES_SECONDS = update_rate  # Every 3 minutes
    dvm_config.UPDATE_DATABASE = update_db
    # Activate these to use a subscription based model instead
    # dvm_config.SUBSCRIPTION_DAILY_COST = 1
    dvm_config.FIX_COST = 0
    dvm_config.CUSTOM_PROCESSING_MESSAGE = processing_msg
    admin_config.LUD16 = dvm_config.LN_ADDRESS

    image = "https://image.nostr.build/3cdd70113e05375e6240f2ecca5d9f4ee783ab386b00cc07ca907b601ab91a85.jpg",
    # Add NIP89
    nip89info = {
        "name": name,
        "picture": image,
        "about": "I show notes that are currently popular all over Nostr. I'm also used for testing subscriptions.",
        "lud16": dvm_config.LN_ADDRESS,
        "supportsEncryption": True,
        "acceptsNutZaps": False,
        "subscription": True,
        "personalized": False,
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

    # admin_config.UPDATE_PROFILE = False
    # admin_config.REBROADCAST_NIP89 = False
    # admin_config.REBROADCAST_NIP88 = False

    # admin_config.FETCH_NIP88 = True
    # admin_config.EVENTID = ""
    # admin_config.PRIVKEY = dvm_config.PRIVATE_KEY

    return DiscoverPeopleWOT(name=name, dvm_config=dvm_config, nip89config=nip89config,
                             nip88config=nip88config, options=options,
                             admin_config=admin_config)


if __name__ == '__main__':
    process_venv(DiscoverPeopleWOT)
