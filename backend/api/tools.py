import random
from backend.data.database import firestore_db


MAX_PROBLEM_ID = 1000  # make this configurable later

async def pick_random_problem_from_db(user, max_id: int = MAX_PROBLEM_ID):
    """
    Try random IDs until we find an existing problem in Firestore.
    """
    attempt = 0
    while True:
        attempt += 1
        rand_id = random.randint(1, max_id)
        print(f"[DEBUG] Attempt {attempt}: trying problem id={rand_id}")

        meta = await firestore_db.get_coding_problems(user, rand_id)  # implement this
        if meta:
            return meta
        # else loop again until we find one
