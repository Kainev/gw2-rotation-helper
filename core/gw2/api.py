import pickle
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


CACHE_FILE = 'cache.pkl'


_cache = {
    'skills': {},
    'professions': {}
}


def _fetch(url, max_retries=5, backoff_factor=0.5):
    session = requests.Session()

    retry = Retry(
        total=max_retries,
        read=max_retries,
        connect=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch data from {url}: {e}")


def _fetch_professions():
    url = "https://api.guildwars2.com/v2/professions?ids=all&v=2019-12-19T00:00:00Z"
    professions = _fetch(url)

    # Transform skills_by_palette tuple array to dictionary for easier palette to skill conversion
    for profession_key in professions.keys():
        profession = professions[profession_key]
        profession['skills_by_palette'] = {pair[0]: pair[1] for pair in profession['skills_by_palette']}

    return professions


def _fetch_skill(skill_id):
    url = f"https://api.guildwars2.com/v2/skills?id={skill_id}"
    return _fetch(url)


def _save_cache():
    global _cache

    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(_cache, f)


def _load_cache():
    global _cache

    try:
        with open(CACHE_FILE, 'rb') as f:
            _cache = pickle.load(f)
    except FileNotFoundError:
        # Initializes as default cache structure, can ignore FileNotFoundError
        pass


def get_skill(skill_id, use_cache=True):
    global _cache

    skill_cache = _cache['skills']

    if skill_id not in skill_cache or not use_cache:
        skill_cache[skill_id] = _fetch_skill(skill_id)
        _save_cache()

    return skill_cache[skill_id]


def get_profession(profession_id, use_cache=True):
    global _cache

    profession_cache = _cache['professions']

    if not profession_cache or not use_cache:
        professions = _fetch_professions()
        for profession in professions:
            profession_cache[profession['code']] = profession
        _save_cache()

    return profession_cache[profession_id]


def skill_id_to_palette_id(skill_id, profession_id):
    skills_by_palette = get_profession(profession_id)['skills_by_palette']

    return next((_palette_id for _skill_id, _palette_id in skills_by_palette.items() if _skill_id == skill_id), None)


def palette_id_to_skill_id(palette_id, profession_id):
    profession = get_profession(profession_id)
    try:
        return profession['skills_by_palette'][palette_id]
    except KeyError:
        return None


_load_cache()
