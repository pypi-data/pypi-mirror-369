use graph::prelude::*;
use crate::common_types::InputInt;

fn create_graph_from(
    vector_of_edges: Vec<(InputInt, InputInt)>
) -> DirectedCsrGraph<InputInt> {
    GraphBuilder::new()
        .csr_layout(CsrLayout::Sorted)
        .edges(vector_of_edges)
        .build()
}

pub fn get_ranking_from(comparisons: Vec<(InputInt, InputInt)>) -> Vec<f32> {
    let (ranking, _iterations, _) = page_rank(
        &create_graph_from(comparisons),
        PageRankConfig::default(),
    );
    ranking
}
