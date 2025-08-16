use snic_core::network::rank;
use snic_core::network::matchup;
use snic_core::network::comparison;
use snic_core::gber::Decomposition;
use snic_core::common_types::{BaseInt, InputInt};

#[test]
fn simple_rank_preserves_sorting() {
    let base: BaseInt = u8::MAX.into();
    let length: InputInt = u8::MAX.into();
    let gber = Decomposition::new(length, base).unwrap();
    let network_matchups = matchup::LocalMatchupsManager::new(gber);
    let matchups = network_matchups.subnetwork_iterators
        .into_iter().flatten().chain(network_matchups.intersubnetwork_matchups)
        .collect::<Vec<Vec<InputInt>>>();
    let mould = comparison::generate_expansion_mould_for(base);
    let pairwise_comparisons = matchups.into_iter()
        .flat_map(|ranking| comparison::convert_to_comparisons(&ranking[..], &mould[..])).collect::<Vec<(InputInt, InputInt)>>();
    let rating = rank::get_ranking_from(pairwise_comparisons);
    let mut sorted_rating = rating.clone();
    sorted_rating.sort_by(|a, b| a.partial_cmp(b).unwrap());
    assert_eq!(sorted_rating, rating);
}
