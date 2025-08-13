import time
from typing import Any, Optional
import numpy as np
import pandas as pd
import warnings

import firebase_admin
from firebase_admin import credentials, firestore
import json


def _sequence_to_db_object(iterable, save=False):
    """
    Helper function to convert an array into a dictionary for a database
    Args:
        iterable: an iterable

    Returns:
        a dict with keys 0, 1, 2..
    Examples:
        A simple range object can be converted into an array of dimension 2:
        >>> _sequence_to_db_object(range(3))
        {0: 0, 1: 1, 2: 2}

        A np.array with more two dimentions
        >>> import numpy as np
        >>> _sequence_to_db_object(np.array([[1, 2], [3, 4], [5, 6]]))
        {0: array([1, 2]), 1: array([3, 4]), 2: array([5, 6])}

        Not iterable
        >>> _sequence_to_db_object(3)
        {0: 3}
    """
    if not hasattr(iterable, "__iter__"):
        return {0: iterable}
    if isinstance(iterable, pd.DataFrame):
        return iterable.reset_index(drop=True).to_dict(orient='index')
    is_int64 = False
    is_float64 = False
    for t in iterable:
        is_int64 = is_int64 or isinstance(t, np.int64)
        is_float64 = is_float64 or isinstance(t, np.float64)
    if is_int64:
        warnings.warn('Converting np.int64 to int to store in Firestore, may loose precision')
    if is_float64:
        warnings.warn('Converting np.float64 to float to store in Firestore, may loose precision')
    return {i: int(t) if isinstance(t, np.integer) else float(t) if isinstance(t,
                                                                               np.floating) else t if isinstance(
        t,
        dict) else json.dumps(
        t) for i, t in enumerate(iterable)}


def _get_collection(
        collection_name: str,
        firebase_credentials: dict
):
    """
    Helper function to get the firebase collection to store conditions and observations

    Args:
        collection_name: the name of the study as given in firebase
        firebase_credentials: dict with the credentials for firebase

    Returns:
        the firebase collection
    """
    # get the firebase collection (name of the study most probably)
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials)
        app = firebase_admin.initialize_app(cred)
    else:
        app = firebase_admin.get_app()
    db = firestore.client()

    return app, db.collection(f"{collection_name}")


def _set_meta(
        seq_col: Any,
        condition_dict: dict,
        doc_meta: str = 'autora_meta',
        is_append: bool = False
):
    """
    Helper function to set the meta-data (start_time and finished for each condition)

    Args:
        seq_col: firebase collection of the experiment
        condition_dict: condition in dict format
        doc_meta: name of the meta document
        is_append: if true, append the conditions instead of resetting them
    """
    doc_ref_meta = seq_col.document(doc_meta)
    meta_dict = _sequence_to_db_object(
        [{"start_time": None, "finished": False}] * len(condition_dict)
    )
    doc = doc_ref_meta.get()
    if is_append and doc.exists:
        data = doc.to_dict()
        last_key = max(map(int, data.keys()))
        meta_dict = {str(key + last_key + 1): value for key, value in meta_dict.items()}
        doc_ref_meta.update(meta_dict)
    else:
        meta_dict = {str(key): value for key, value in meta_dict.items()}
        doc_ref_meta.set(meta_dict)


def set_meta(
        collection_name: str,
        condition: Any,
        firebase_credentials: dict,
        doc_meta: str = 'autora_meta',
        is_append: bool = False
):
    """
    Standalone function to set the meta-data for (start_time and finished for each condition)
    Args:
        collection_name: the name of the study as given in firebase
        condition: the condition to run
        firebase_credentials: dict with the credentials for firebase
        doc_meta: document to store metadata
        is_append: if true, append the conditions instead of resetting them
    """
    app, seq_col = _get_collection(collection_name, firebase_credentials)
    condition_dict = _sequence_to_db_object(condition)
    seq_col.document(doc_meta).delete()
    _set_meta(seq_col, condition_dict, doc_meta, is_append)
    firebase_admin.delete_app(app)


def __reset_col(
        parent_col,
        doc,
        col
):
    doc_ref = parent_col.document(doc)
    col_ref = doc_ref.collection(col)
    docs = col_ref.stream()
    for d in docs:
        d.reference.delete()


def _reset_out(
        seq_col: Any,
        doc_out: str = 'autora_out',
        col_observation: str = 'observations'):
    """
    Helper function to reset the observations

    Args:
        seq_col: firebase collection of the experiment
        doc_out: document to store out data
        col_observation: collection to store the observations
    """
    __reset_col(seq_col, doc_out, col_observation)


def _reset_in(
        seq_col: Any,
        doc_in: str = 'autora_in',
        col_condition: str = 'conditions'
):
    """
    Helper function to reset the conditions

    Args:
        seq_col: firebase collection of the experiment
        doc_in: document to store in data
        col_condition: collection to store the conditions
    """
    __reset_col(seq_col, doc_in, col_condition)


def _set_up_experiment_db(
        seq_col: Any,
        condition_dict: dict,
        doc_out: str = 'autora_out',
        doc_in: str = 'autora_in',
        col_observation: str = 'observations',
        col_condition: str = 'conditions',
        is_append: bool = False
):
    """
    Helper function to set up the conditions and observation database
    Args:
        seq_col: firebase collection of the experiment
        condition_dict: condition in dict format
        doc_out: document to store out data
        doc_in: document to store in data
        col_observation: collection to store the observations
        col_condition: collection to store the conditions
        is_append: if true, append the conditions and observations instead of resetting them
    """
    doc_ref_out = seq_col.document(doc_out)
    doc_ref_in = seq_col.document(doc_in)
    last_key = 0
    if is_append:
        condition_ref = doc_ref_in.collection(col_condition)
        documents_condition = list(condition_ref.list_documents())
        last_key = len(documents_condition) + 1
    else:
        _reset_in(seq_col, doc_in, col_condition)
        _reset_out(seq_col, doc_out, col_observation)
    for key in condition_dict:
        key_tmp = key + last_key
        doc_ref_in.collection(col_condition).document(str(key_tmp)).set(
            {str(key_tmp): condition_dict[key]}
        )
        doc_ref_out.collection(col_observation).document(str(key_tmp)).set({str(key_tmp): None})


def set_up_experiment_db(
        collection_name: str,
        condition: Any,
        firebase_credentials: dict,
        doc_out: str = 'autora_out',
        doc_in: str = 'autora_in',
        col_observation: str = 'observations',
        col_condition: str = 'conditions',
        is_append: bool = False
):
    """
    Standalone function to set up a db with conditions and observations.
    Use send_conditions instead if you want to use in a cycle

        WARNING: Does not rest the database and does not set up meta-data for
        the communication to an autora workflow.

    Args:
        collection_name: the name of the study as given in firebase
        condition: the condition to run
        firebase_credentials: dict with the credentials for firebase
        doc_out: document to store out data
        doc_in: document to store in data
        col_observation: collection to store the observations
        col_condition: collection to store the conditions
        is_append: if true, append the conditions and observations instead of resetting them
    """
    app, seq_col = _get_collection(collection_name, firebase_credentials)
    condition_dict = _sequence_to_db_object(condition)
    _set_up_experiment_db(seq_col, condition_dict, doc_out, doc_in, col_observation, col_condition,
                          is_append)
    firebase_admin.delete_app(app)


def send_conditions(
        collection_name: str,
        conditions: Any,
        firebase_credentials: dict,
        doc_meta: str = "autora_meta",
        doc_out: str = "autora_out",
        doc_in: str = "autora_in",
        col_observation: str = "observations",
        col_condition: str = "conditions",
        is_append: bool = False
):
    """
    Upload a new set of conditions, prepare the database for observations, and set up
    meta-data for communication with autora cycle.

    Args:
        collection_name: the name of the study as given in firebase
        conditions: the condition to run
        firebase_credentials: dict with the credentials for firebase
        doc_meta: document to store metadata
        doc_out: document to store out data
        doc_in: document to store in data
        col_observation: collection to store the observations
        col_condition: collection to store the conditions
        is_append: if true, append the conditions, observations and meta-data instead of resetting them
    """

    # get the conditions with their indexes
    condition_dict = _sequence_to_db_object(conditions)

    # get the firebase collection
    app, seq_col = _get_collection(collection_name, firebase_credentials)

    # set the meta data
    _set_meta(seq_col, condition_dict, doc_meta, is_append)

    # setup db for conditions and observations
    _set_up_experiment_db(seq_col, condition_dict, doc_out, doc_in, col_observation, col_condition,
                          is_append)

    firebase_admin.delete_app(app)


def get_observations(collection_name: str,
                     firebase_credentials: dict,
                     doc_out: str = "autora_out",
                     col_observation: str = "observations", ) -> Any:
    """
    get observations from firestore database

    Args:
        collection_name: name of the collection as given in firebase
        firebase_credentials: credentials for firebase
        doc_out: document to store out data
        doc_out: document to store out data
        col_observation: collection to store the observations

    Returns:
        observations
    """

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials)
        app = firebase_admin.initialize_app(cred)
    else:
        app = firebase_admin.get_app()
    db = firestore.client()
    seq_col = db.collection(f"{collection_name}")

    doc_ref_out = seq_col.document(doc_out)

    col_ref = doc_ref_out.collection(col_observation)
    docs = col_ref.stream()
    observations = {}
    for doc in docs:
        observations.update(doc.reference.get().to_dict())
    firebase_admin.delete_app(app)
    return observations


def check_firebase_status(
        collection_name: str, firebase_credentials: dict, time_out: Optional[int] = None,
        pids_aborted: list = []
) -> str:
    """
    check the status of the condition

    Args:
        collection_name: name of the collection as given in firebase
        firebase_credentials: credentials for firebase
        time_out: time out for participants that started the condition
            but didn't finish (after this time spots are freed)
        pids_aborted: a list of personal ids that aborted the experiment (free the places)

    Returns:
        Can have three different outcomes:
            (1) available -> no action needed, recruitment should be started (if paused)
            (2) finished -> collection of observations is finished
            (3) unavailable -> all conditions are running, recruitment should be paused
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials)
        app = firebase_admin.initialize_app(cred)
    else:
        app = firebase_admin.get_app()
    db = firestore.client()
    seq_col = db.collection(f"{collection_name}")

    doc_ref_meta = seq_col.document("autora_meta")
    meta_data = doc_ref_meta.get().to_dict()

    finished = True
    available = False
    for key, value in meta_data.items():
        # return available if there are conditions that haven't been started
        if value["start_time"] is None and not value["finished"]:
            available = True
        else:
            if not value["finished"]:
                unix_time_seconds = int(time.time())
                time_from_started = unix_time_seconds - value["start_time"]
                is_aborted = False
                if "pId" in value:
                    is_aborted = value['pId'] in pids_aborted
                if is_aborted:
                    doc_ref_meta.update({key: {"start_time": None, "finished": False, "pId": None}})
                    available = True
                else:
                    finished = False
    firebase_admin.delete_app(app)
    if available:
        return 'available'
    if finished:
        # if all start_times are set and have data, condition is finished
        return "finished"
    # if all start_times are set, but there is no data for all of them, pause the condition
    return "unavailable"



