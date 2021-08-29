"""import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://admin:G5F9udcUBYtg4eZ@cluster0.vuvdy.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.test
print(db)"""
# https://forum.rasa.com/t/custom-tracker-to-save-conversation-history-into-firebase-firestore/35432

import itertools

from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Text,
)

from pymongo.database import Database
from pymongo import MongoClient
from pymongo.collection import Collection
from rasa_sdk import Tracker

from credentials import host, username, password, db

from rasa.core.brokers.broker import EventBroker
from rasa.shared.core.domain import Domain
from rasa.shared.core.events import (
    SessionStarted,
    UserUttered,
    BotUttered,
    ActionExecuted
)
from rasa.shared.core.trackers import (
    DialogueStateTracker,
    EventVerbosity,
)
from rasa.core.tracker_store import TrackerStore


class MongoTrackerStore(TrackerStore):
    """Stores conversation history in Mongo.
    Property methods:
        conversations: returns the current conversation
    """

    def __init__(
            self,
            domain: Domain,
            # host: Optional[Text] = "mongodb://localhost:27017",
            # db: Optional[Text] = "rasa",
            # username: Optional[Text] = None,
            # password: Optional[Text] = None,
            auth_source: Optional[Text] = "admin",
            collection: Optional[Text] = "conversations",
            event_broker: Optional[EventBroker] = None,
            **kwargs: Dict[Text, Any],
    ) -> None:
        self.client = MongoClient(
            host,
            username=username,
            password=password,
            authSource=auth_source,
            # delay connect until process forking is done
            connect=False,
        )

        self.db = Database(self.client, db)
        self.collection = collection
        super().__init__(domain, event_broker, **kwargs)

        self._ensure_indices()

    @property
    def conversations(self) -> Collection:
        """Returns the current conversation."""
        return self.db[self.collection]

    def _ensure_indices(self) -> None:
        """Create an index on the sender_id."""
        self.conversations.create_index("sender_id")

    @staticmethod
    def _current_tracker_state_without_events(tracker: DialogueStateTracker) -> Dict:
        # get current tracker state and remove `events` key from state
        # since events are pushed separately in the `update_one()` operation
        state = tracker.current_state(EventVerbosity.ALL)
        state.pop("events", None)

        return state

    def save(self, tracker: DialogueStateTracker) -> None:
        """Saves the current conversation state."""
        if self.event_broker:
            self.stream_events(tracker)

        additional_events = self._additional_events(tracker)

        #print([e.as_dict() for e in additional_events if type(e) == UserUttered or type(e) == BotUttered])
        updateUserDBInfo(tracker)

        self.conversations.update_one(
            {"sender_id": tracker.sender_id},
            {
                "$set": self._current_tracker_state_without_events(tracker),
                "$push": {
                    "events": {"$each": [e.as_dict() for e in additional_events]}
                },
            },
            upsert=True,
        )

        updateEmotionStats(tracker)

    def _additional_events(self, tracker: DialogueStateTracker) -> Iterator:
        """Return events from the tracker which aren't currently stored.
        Args:
            tracker: Tracker to inspect.
        Returns:
            List of serialised events that aren't currently stored.
        """

        stored = self.conversations.find_one({"sender_id": tracker.sender_id}) or {}
        all_events = self._events_from_serialized_tracker(stored)

        number_events_since_last_session = len(
            self._events_since_last_session_start(all_events)
        )

        return itertools.islice(
            tracker.events, number_events_since_last_session, len(tracker.events)
        )

    @staticmethod
    def _events_from_serialized_tracker(serialised: Dict) -> List[Dict]:
        return serialised.get("events", [])

    @staticmethod
    def _events_since_last_session_start(events: List[Dict]) -> List[Dict]:
        """Retrieve events since and including the latest `SessionStart` event.
        Args:
            events: All events for a conversation ID.
        Returns:
            List of serialised events since and including the latest `SessionStarted`
            event. Returns all events if no such event is found.
        """

        events_after_session_start = []
        for event in reversed(events):
            events_after_session_start.append(event)
            if event["event"] == SessionStarted.type_name:
                break

        return list(reversed(events_after_session_start))

    def _retrieve(
            self, sender_id: Text, fetch_events_from_all_sessions: bool
    ) -> Optional[List[Dict[Text, Any]]]:
        stored = self.conversations.find_one({"sender_id": sender_id})

        # look for conversations which have used an `int` sender_id in the past
        # and update them.
        if not stored and sender_id.isdigit():
            from pymongo import ReturnDocument

            stored = self.conversations.find_one_and_update(
                {"sender_id": int(sender_id)},
                {"$set": {"sender_id": str(sender_id)}},
                return_document=ReturnDocument.AFTER,
            )

        if not stored:
            return None

        events = self._events_from_serialized_tracker(stored)

        if not fetch_events_from_all_sessions:
            events = self._events_since_last_session_start(events)

        return events

    def retrieve(self, sender_id: Text) -> Optional[DialogueStateTracker]:
        """Retrieves tracker for the latest conversation session."""
        events = self._retrieve(sender_id, fetch_events_from_all_sessions=False)

        if not events:
            return None

        return DialogueStateTracker.from_dict(sender_id, events, self.domain.slots)

    def retrieve_full_tracker(
            self, conversation_id: Text
    ) -> Optional[DialogueStateTracker]:
        """Fetching all tracker events across conversation sessions."""
        events = self._retrieve(conversation_id, fetch_events_from_all_sessions=True)

        if not events:
            return None

        return DialogueStateTracker.from_dict(
            conversation_id, events, self.domain.slots
        )

    def keys(self) -> Iterable[Text]:
        """Returns sender_ids of the Mongo Tracker Store."""
        return [c["sender_id"] for c in self.conversations.find()]


def setUserDBConversation(user_db_name, tracker):
    client = MongoClient(host, username=username, password=password, authSource='admin', connect=False)
    database = Database(client, db)
    colec = database['users']

    existsDocument = colec.find_one({"name": user_db_name})
    if existsDocument is None:
        print('User created')
        userDocument = {
            "name": user_db_name,
            "conversations": tracker.sender_id
        }
        colec.insert_one(userDocument)
    else:
        print('User found')
        colec.update_one({"name": user_db_name}, {"$addToSet": {"conversations": tracker.sender_id}})


def updateUserDBInfo(tracker: Tracker):
    client = MongoClient(host, username=username, password=password, authSource='admin', connect=False)
    database = Database(client, db)
    colec = database['users']

    user_db_name = tracker.get_slot('user_db_name')
    if user_db_name is not None:
        for key in tracker.slots:
            if key != 'session_started_metadata' and key != 'user_db_name':
                if tracker.get_slot(key) is not None:
                    colec.update_one({"name": user_db_name}, {"$set": {key: tracker.get_slot(key)}})

def updateEmotionStats(tracker: Tracker):
    stat = tracker.get_slot('emotion_stats')
    for entity in tracker.latest_message['entities']:
        if entity['entity'] == 'emotion':
            emotions = entity['labels']
    
    # if stat^ + less | - more
    # if statv + more | - less
    # -0.5 stat 0.5 -> +-0.25*percentage
    # ^⁺0.5 stat -> +0.25*percentage | -0.25*percentage
    # v-0.5 stat -> -0.25*percentage | +0.25*percentage
    for label in emotions:
        if label['label'] in ['joy', 'love', 'surprise']:
            score = label['score']
            if stat >= 0:
                if label['label'] == 'love':
                    score = score/2
                if label['label'] == 'surprise':
                    score = score/3
                # stat + ((1 - stat) * 0.5*score)
                stat += ((1 - stat) * 0.5*score)
            else:
                if label['label'] == 'love':
                    score = score/2
                if label['label'] == 'surprise':
                    score = score/3
                # if stat < 0: stat + ((0.5 - stat) * 0.5*score)
                stat += ((0.5 - stat) * 0.5*score)    
        elif label['label'] in ['sadness', 'fear', 'anger']:
            if stat <= 0:
                if label['label'] == 'anger':
                    score = score/2
                if label['label'] == 'fear':
                    score = score/3
                # stat - ((1 + stat) * 0.5*percentatge)
                stat -= ((1 + stat) * 0.5*score)
            else:
                if label['label'] == 'anger':
                    score = score/2
                if label['label'] == 'fear':
                    score = score/3
                # if stat > 0: stat - ((0.5 + stat) * 0.5*score)
                stat -= ((0.5 + stat) * 0.5*score)

    tracker.add_slots(stat)