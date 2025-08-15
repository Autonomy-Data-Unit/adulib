# %% [markdown]
# # str_matching
#
# > Utils for finding the closest match of a string in a list of strings.

# %%
#|default_exp algos.str_matching

# %%
#|hide
import nblite; from nblite import show_doc; nblite.nbl_export()
import adulib.algos.str_matching as this_module

# %%
#|export
try:
    import rapidfuzz
    import numpy as np
except ImportError as e:
    raise ImportError(f"Install adulib[algos] to use this API.") from e

# %%
#|hide
from adulib.llm import set_call_log_save_path
from adulib.caching import set_default_cache_path
repo_path = nblite.config.get_project_root_and_config()[0]
set_default_cache_path(repo_path / '.tmp_cache')
set_call_log_save_path(repo_path / '.call_logs.jsonl') 

# %%
#|hide
show_doc(this_module.fuzzy_match)


# %%
#|export
def fuzzy_match(query_string, candidate_strings, max_results=5, min_similarity=0, scorer=rapidfuzz.fuzz.ratio):
    """
    Find the closest fuzzy matches to a query string from a list of candidate strings using RapidFuzz.
    
    This is a simplified wrapper around `rapidfuzz.process.extract` to find fuzzy matches. The equivalent of, and much faster version of, `difflib.get_close_matches`.

    Args:
        query_string (str): The string to match against the candidates.
        candidate_strings (Iterable[str]): The list of candidate strings to search.
        max_results (int, optional): Maximum number of matches to return. Defaults to 8.
        min_similarity (float, optional): Minimum similarity threshold (0.0-1.0). Defaults to 0.1.
        scorer (callable, optional): Scoring function from rapidfuzz.fuzz. Defaults to rapidfuzz.fuzz.ratio. See rapidfuzz.fuzz for available scorers.

    Returns:
        List[Tuple[str, float, int]]: List of tuples containing (matched_string, score, index).
    """
    results = rapidfuzz.process.extract(
        query_string,
        candidate_strings,
        scorer=rapidfuzz.fuzz.ratio,
        limit=max_results,
        score_cutoff=min_similarity * 100 # rapidfuzz scores are 0-100, so cutoff needs to be scaled
    )
    return results


# %%
fuzzy_match(
    "Apple Inc",
    ["Apple Inc", "Apple", "Google LLC", "Microsoft Corp"],
)

# %%
#|hide
show_doc(this_module.get_vector_dist_matrix)


# %%
#|export
def get_vector_dist_matrix(
    vectors:list[list[float]],
    metric:str="cosine",
):
    """
    Calculate the pairwise distance matrix for a set of vectors.

    Args:
        vectors (List[List[float]]): List of vectors to calculate distances for.
        metric (str, optional): Distance metric to use. Defaults to "cosine". Options include "euclidean", "manhattan", "cosine", etc. See sklearn.metrics.pairwise_distances for more options.

    Returns:
        np.ndarray: Distance matrix. Each element [i, j] represents the distance between vectors[i] and vectors[j].
    """
    from sklearn.metrics import pairwise_distances
    return pairwise_distances(vectors, metric=metric)


# %%
vs = [
    [9,7,1,2,6],
    [1,8,3,3,2],
    [4,5,6,7,8]
]
get_vector_dist_matrix(vs)

# %%
#|hide
show_doc(this_module.embedding_match)


# %%
#|export
def embedding_match(embedding_index, dist_matrix, num_matches=5):
    """
    Find the indices and distances of the closest matches to a given embedding. Use it in combination with `get_vector_dist_matrix` to find the closest embeddings.

    Args:
        embedding_index (int): Index of the embedding to match.
        dist_matrix (np.ndarray): Pairwise distance matrix of embeddings. Computed using `get_vector_dist_matrix`.
        num_matches (int, optional): Number of closest matches to return (excluding self). Defaults to 5.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Tuple of (indices of closest matches, distances to those matches).
    """
    distances = dist_matrix[embedding_index]
    closest_indices = np.argsort(distances)[1:num_matches+1]
    closest_distances = [distances[i] for i in closest_indices]
    return closest_indices, np.array(closest_distances)


# %%
from adulib.llm import async_batch_embeddings
docs = [
    "Apple Inc",
    "Apple",
    "Google LLC",
    "Microsoft Corp",
    "Apple Inc is a technology company.",
    "Google is a search engine.",
    "Microsoft develops software and hardware.",
    "Apple and Google are competitors in the tech industry."
]
embeddings, responses = await async_batch_embeddings(
    model="text-embedding-3-small",
    input=docs,
    batch_size=1000,
    verbose=False,
)
dist_matrix = get_vector_dist_matrix(embeddings)
match_indices, _ = embedding_match(docs.index("Apple"), dist_matrix, num_matches=2)
[docs[i] for i in match_indices]
