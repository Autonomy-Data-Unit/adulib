# %% [markdown]
# # algos.smart_dedup
#
# > An entity deduplication algorithm that uses a combination of fuzzy string matching, vector embeddings, and LLM-based selection to identify duplicates in a list of entities.

# %%
#|default_exp algos._smart_dedup
#|export_as_func true

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.algos._smart_dedup as this_module
from adulib.algos import smart_dedup

# %%
#|top_export
import inspect
from pydantic import BaseModel
from adulib.algos.str_matching import fuzzy_match, get_vector_dist_matrix, embedding_match
from adulib.llm import async_batch_embeddings
import rapidfuzz
from tqdm.asyncio import tqdm_asyncio
import asyncio

# %%
#|hide
show_doc(smart_dedup)


# %%
#|set_func_signature
async def smart_dedup(
    entities: list[str],
    embedding_model: str,
    match_selection_model: str,
    max_fuzzy_str_matches: int = 5,
    min_fuzzy_str_match_score: float = 0,
    fuzzy_str_match_scorer=rapidfuzz.fuzz.ratio,
    num_embedding_matches: int = 5,
    embedding_batch_size: int = 1000,
    match_selection_temperature: float = 0.0,
    system_prompt: str = None,
    prompt_template: str = None,
    verbose: bool = False,
):
    """
    Entity deduplication of a list of strings using fuzzy string matching and embedding-based similarity, 
    followed by model-assisted duplicate selection.
    
    Args:
        entities (list[str]): List of entity strings to deduplicate.
        embedding_model (str): Name or path of the embedding model to use.
        match_selection_model (str): Model identifier for selecting matches among candidates.
        max_fuzzy_str_matches (int, optional): Maximum number of fuzzy string match candidates per entity. Defaults to 5.
        min_fuzzy_str_match_score (float, optional): Minimum similarity score for fuzzy string matches. Defaults to 0.
        fuzzy_str_match_scorer (callable, optional): Scoring function for fuzzy string matching. Defaults to rapidfuzz.fuzz.ratio.
        num_embedding_matches (int, optional): Number of embedding-based match candidates per entity. Defaults to 5.
        embedding_batch_size (int, optional): Batch size for embedding computation. Defaults to 1000.
        match_selection_temperature (float, optional): Temperature parameter for match selection model. Defaults to 0.0.
        system_prompt (str, optional): Optional system prompt for the match selection model.
        prompt_template (str, optional): Optional prompt template for the match selection model.
        verbose (bool, optional): If True, displays progress bars and additional output. Defaults to False.
        
    Returns:
        tuple[list[list[tuple[str, str]]], list[str]]:
            - List of disconnected subgraphs, each representing a group of duplicate entities.
            - List of entities without any detected matches.
    Notes:
        See `adulib.algos._dedup.system_prompt` and `adulib.algos._dedup.prompt_template` for prompt details.
    """
    ...


# %%
#|hide
from adulib.llm import set_call_log_save_path
from adulib.caching import set_default_cache_path
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')
set_call_log_save_path(repo_path / '.call_logs.jsonl') 

# %%
entities = [
    "Lockheed Martin",
    "Raytheon Technologies",
    "Northrop Grumman",
    "BAE Systems",
    "Boeing Defense",
    "General Dynamics",
    "Thales Group",
    "Leonardo S.p.A.",
    "Rheinmetall AG",
    "Elbit Systems",
    "Saab AB",
    "MBDA",
    "Hanwha Defense",
    "Israel Aerospace Industries",
    "Naval Group",
    # Duplicates for testing deduplication
    "Lockheed Martin Corporation",
    "Lockeed Martin Corp.",
    "Raytheon",
    "Northrop Grumman Corp.",
    "BAE Systems plc",
    "Boeing Defense, Space & Security",
    "General Dynamics Corporation",
    "Thales",
    "Leonardo",
    "Rheinmetall",
    "Elbit",
    "Saab",
    "MBDA Missile Systems",
    "Hanwha",
    "IAI",
    "Naval Group SA",
    # Additional entity without a duplicate
    "General Atomics",
]
embedding_model="text-embedding-3-small"
match_selection_model="gpt-4.1-mini"
max_fuzzy_str_matches = 1
min_fuzzy_str_match_score = 0
fuzzy_str_match_scorer = rapidfuzz.fuzz.ratio
num_embedding_matches = 1
embedding_batch_size = 1000
match_selection_temperature = 0.0
system_prompt = None
prompt_template = None
verbose = False

# %% [markdown]
# ## Find duplicate candidates using `adulib.algos.fuzzy_match`

# %%
#|export
_entities = set(entities)
entities = list(_entities)

fuzzy_match_candidates = [
    [
        candidate for candidate, _, _, in
        fuzzy_match(entity, _entities - {entity}, max_results=max_fuzzy_str_matches, min_similarity=min_fuzzy_str_match_score, scorer=fuzzy_str_match_scorer)
    ] for entity in entities
]

# %% [markdown]
# ## Find duplicate candidates using `adulib.algos.embedding_match`

# %%
#|export
embeddings = await async_batch_embeddings(
    model=embedding_model,
    input=entities,
    batch_size=1000,
    verbose=verbose,
)

dist_matrix = get_vector_dist_matrix(embeddings, metric='cosine')

embedding_match_candidates = [
    [entities[match_i] for match_i in embedding_match(i, dist_matrix, num_matches=num_embedding_matches)[0]]
    for i in range(len(entities))
]

# %% [markdown]
# ## Select duplicates using LLMs

# %%
#|top_export
system_prompt = inspect.cleandoc("""
You are an expert in entity deduplication. You will be shown a string and a list of similar-looking strings (some may be aliases, abbreviations, misspellings, or closely related variants, while others may be unrelated).

Your task is to identify which strings refer to the same entity as the reference. Return a Python list of **0-based indices** corresponding to the matching entries. Only include strings that could realistically refer to the same entity. Do not include unrelated strings. Do not explain your reasoning. If no strings match, return an empty list.
""".strip())

prompt_template = inspect.cleandoc("""
Entity: {entity}

Entity duplicate candidates:
{duplicate_candidates}
""".strip())

class Duplicates(BaseModel):
    duplicate_indices: list[int]


# %%
#|top_export
async def select_duplicates(entity: str, duplicate_candidates: list[str], model, temperature):
    """
    Use an LLM to select which candidates from a list are duplicates of a given entity.

    Args:
        entity (str): The reference entity string.
        duplicate_candidates (list[str]): List of candidate strings to check for duplication.
        model: The LLM model to use.
        temperature: Sampling temperature for the LLM.

    Returns:
        tuple: (indices of matches in duplicate_candidates, matched candidate strings, sorted candidate list)
    """
    import adulib.llm
    import json
    
    duplicate_candidates = sorted(set(duplicate_candidates)) # This ensures consistent caching.

    res = await adulib.llm.async_single(
        model=model,
        system=system_prompt,
        prompt=prompt_template.format(
            entity=entity,
            duplicate_candidates="\n".join([f"{i}. {m}" for i, m in enumerate(duplicate_candidates, start=0)]),
        ),
        temperature=temperature,
        response_format=Duplicates,
    )
    
    match_indices = Duplicates(**json.loads(res)).duplicate_indices
    return [duplicate_candidates.index(duplicate_candidates[i]) for i in match_indices], [duplicate_candidates[i] for i in match_indices]


# %%
#|export
tasks = [
    select_duplicates(entity, set(fuzzy_candidates+embedding_candidates), match_selection_model, match_selection_temperature)
    for entity, fuzzy_candidates, embedding_candidates in zip(entities, fuzzy_match_candidates, embedding_match_candidates)
]

if verbose:
    results = await tqdm_asyncio.gather(*tasks, desc="Selecting duplicates", total=len(tasks))
else:
    results = await asyncio.gather(*tasks)
  
matches = []  
entities_without_matches = []
for entity, matched_entities in zip(entities, results):
    matches.extend([(entity, matched_entity) for matched_entity in matched_entities[1]])
    if len(matched_entities[1]) == 0:
        entities_without_matches.append(entity)


# %% [markdown]
# ## Find disconnected subgraphs in the matched pairs

# %%
#|top_export
def find_disconnected_subgraphs(matches):
    """
    Given a list of pairwise matches (edges), find all disconnected subgraphs (connected components).

    Args:
        matches (list of tuple): List of pairs representing edges between nodes.

    Returns:
        list of set: Each set contains the nodes in one connected component.
    """
    from collections import defaultdict

    # Create a graph from the matches
    graph = defaultdict(set)
    for item1, item2 in matches:
        graph[item1].add(item2)
        graph[item2].add(item1)

    visited = set()
    subgraphs = []

    def dfs(node, current_subgraph):
        stack = [node]
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                current_subgraph.add(current)
                stack.extend(graph[current] - visited)

    # Find all disconnected subgraphs
    for node in graph:
        if node not in visited:
            current_subgraph = set()
            dfs(node, current_subgraph)
            subgraphs.append(current_subgraph)
            
    subgraphs = sorted([tuple(sorted(subgraph)) for subgraph in subgraphs]) # Sorting ensures consistent output

    return subgraphs


# %%
#|func_return
find_disconnected_subgraphs(matches), entities_without_matches
