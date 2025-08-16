//! Python bindings for the snic library.
use snic_core::{common_types, gber, network};
use pyo3::prelude::*;

/// Generate all matchups of a network of a given size.
/// TODO: stream instead of collecting all in memory.
#[pyfunction]
#[pyo3(signature = (network_size, match_size))]
fn stream_matches_from<'py>(
    _py: Python<'py>,
    network_size: common_types::InputInt,
    match_size: common_types::BaseInt,
) -> Vec<Vec<common_types::InputInt>> {
    let decomposition =
        gber::Decomposition::new(network_size, match_size).expect("Invalid decomposition values");
    let matchups_manager = network::matchup::LocalMatchupsManager::new(decomposition);
    matchups_manager.intersubnetwork_matchups
        .into_iter().chain(
            matchups_manager.subnetwork_iterators
                .into_iter().flatten()
        ).collect()
}


#[pyfunction]
#[pyo3(signature = (ranked_matches))]
fn stream_rankings_from<'py>(
    _py: Python<'py>,
    ranked_matches: Vec<Vec<common_types::InputInt>>,
) -> Vec<common_types::InputInt> {
    let expansion_mould =
        network::comparison::generate_expansion_mould_for(
            ranked_matches[0].len() as common_types::BaseInt
    );
    let pairwise_comparisons = ranked_matches.into_iter()
        .flat_map(
            |ranking| {
                network::comparison::convert_to_comparisons(
                    &ranking[..],
                    &expansion_mould[..],
                )
            }
        ).collect::<Vec<(common_types::InputInt, common_types::InputInt)>>();
    let rank_scores = network::rank::get_ranking_from(pairwise_comparisons);
    let mut indices = (0..(rank_scores.len() as common_types::InputInt))
        .collect::<Vec<common_types::InputInt>>();
    indices.sort_by(|a, b| rank_scores[*a as usize].partial_cmp(&rank_scores[*b as usize]).unwrap());
    indices
}

#[pymodule]
fn snic(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(stream_matches_from, m)?)?;
    m.add_function(wrap_pyfunction!(stream_rankings_from, m)?)?;
    Ok(())
}

