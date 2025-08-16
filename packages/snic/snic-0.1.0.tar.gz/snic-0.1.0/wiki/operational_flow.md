# SNIC Operational Flow

## Introduction

The Sparse Network of Idempotent Comparisons (SNIC) algorithm operates through a series of well-defined steps, from the initial generation of matchups to the final ranking process. This page outlines the operational flow of SNIC, providing insights into how the algorithm efficiently processes and ranks large sets of elements.

## Matchup Generation Process

The first step in SNIC's operational flow is the generation of matchups. This process is deterministic and based on the network structure defined by the GBER decomposition.

### Steps in Matchup Generation

1. **GBER Decomposition**: The total number of elements is decomposed using GBER, determining the subnetwork sizes.
2. **Subnetwork Initialization**: For each term in the GBER decomposition, a subnetwork is created.
3. **Stride-Based Algorithm**: Within each subnetwork, matchups are generated using a stride-based algorithm.

### Stride-Based Algorithm

For a subnetwork of size b^p (where b is the base):
1. The algorithm runs for p rounds.
2. In each round r (starting from 1), the stride length is b^(p-r).
3. Elements are grouped into matchups based on the current stride.

### Example

For a base-2 subnetwork of size 8 (2^3):
- Round 1 (stride 4): (0,4), (1,5), (2,6), (3,7)
- Round 2 (stride 2): (0,2), (1,3), (4,6), (5,7)
- Round 3 (stride 1): (0,1), (2,3), (4,5), (6,7)

This process ensures a diverse and comprehensive set of comparisons within each subnetwork.

[Learn how GBER shapes these subnetworks](gber.md#gber-in-snic)

## Base-Sized Matchups

A key feature of SNIC is its use of base-sized matchups, which contribute to its efficiency and effectiveness.

### Properties of Base-Sized Matchups

1. **Size**: Each matchup contains exactly b elements, where b is the chosen base for the SNIC system.
2. **Consistency**: The size of matchups is constant throughout the entire SNIC network.
3. **Information Density**: Each matchup provides b(b-1)/2 pairwise comparisons, maximizing information gain.

### Advantages of Base-Sized Matchups

1. **Efficient Information Gathering**: Multiple pairwise comparisons are derived from a single matchup evaluation.
2. **Scalability**: The fixed size allows for consistent processing regardless of the total number of elements.
3. **Flexibility**: The base can be chosen to balance between matchup complexity and network depth.

[Explore how base choice affects SNIC's structure](network_structure.md#hub-and-spoke-model)

## Comparison Derivation

After matchups are generated and evaluated, SNIC derives pairwise comparisons from the matchup results.

### Process of Deriving Comparisons

1. **Matchup Evaluation**: Each matchup is ranked externally (e.g., by human judgment or an automated system).
2. **Pairwise Extraction**: From each ranked matchup of size b, b(b-1)/2 pairwise comparisons are extracted.
3. **Directed Comparison Creation**: For each pair (i, j) in the matchup:
   - If i is ranked higher than j, a comparison "i beats j" is created
   - If j is ranked higher than i, a comparison "j beats i" is created

### Example

For a base-3 matchup (A, B, C) ranked as [B, A, C]:
- Derived comparisons: "B beats A", "B beats C", "A beats C"

This process transforms the ranked matchups into a set of directed pairwise comparisons, which form the basis for the comparison graph.

## Properties of Derived Comparisons

The comparisons derived from SNIC matchups have several important properties that contribute to the algorithm's effectiveness.

### Key Properties

1. **Directed**: Each comparison has a clear winner and loser, providing unambiguous ranking information.
2. **Unique**: Within the context of the entire network, each pair of elements is compared at most once, ensuring efficiency.
3. **Consistent Within Matchups**: The derived comparisons always align with the ranking within each matchup.
4. **Transitive Within Matchups**: If A beats B and B beats C in a matchup, then A necessarily beats C.
5. **Sparse**: The total number of comparisons is much smaller than in a complete tournament, especially for large datasets.

These properties ensure that SNIC generates a rich yet efficient set of comparisons for ranking.

## Comparison Graph Construction

The derived pairwise comparisons are used to construct a directed graph that represents the overall comparison structure.

### Graph Construction Process

1. **Nodes**: Each element in the SNIC network becomes a node in the graph.
2. **Edges**: Each comparison becomes a directed edge from the winner to the loser.
3. **Edge Weights**: Typically, all edges have equal weight, representing a single win.

### Properties of the Comparison Graph

1. **Sparsity**: The graph is much sparser than a complete tournament graph, reflecting SNIC's efficiency.
2. **Subnetwork Structure**: The graph retains the subnetwork structure from the original SNIC network.
3. **Potential for Cycles**: Unlike the matchup rankings, the overall graph may contain cycles (A beats B, B beats C, C beats A).
4. **Hub-and-Spoke Connections**: The graph includes edges representing inter-subnetwork comparisons based on the hub-and-spoke model.

This graph serves as the foundation for the final ranking process.

## Ranking Algorithm

The final step in SNIC's operational flow is the application of a ranking algorithm to the comparison graph.

### Current Status

As of 2024, the development of a specialized ranking algorithm for SNIC is an active area of research. The unique structure of SNIC's comparison graph presents both challenges and opportunities for ranking algorithm design.

### Potential Approaches

1. **Adaptation of Existing Algorithms**: Algorithms like PageRank could be adapted to work with SNIC's unique graph structure.
2. **Hierarchical Ranking**: Leveraging the subnetwork structure to perform local rankings first, then combining them for a global ranking.
3. **Iterative Methods**: Developing iterative algorithms that propagate ranking information through the sparse network structure.

### Considerations for SNIC Ranking

1. **Handling Cycles**: The ranking algorithm must be able to handle potential cycles in the comparison graph.
2. **Leveraging Sparsity**: Efficient algorithms that can work with SNIC's sparse graph structure are crucial.
3. **Balancing Local and Global Information**: The algorithm should effectively combine strong local rankings within subnetworks with the global information provided by hub-and-spoke connections.

[Explore current challenges and future directions in SNIC ranking](future_directions.md)

## Conclusion

SNIC's operational flow, from matchup generation to the final ranking process, is designed to efficiently handle large-scale ranking tasks. By leveraging its unique network structure, base-sized matchups, and sparse comparison graph, SNIC provides a framework for generating meaningful rankings with significantly fewer comparisons than traditional methods.

## See Also
- [SNIC Network Structure](network_structure.md)
- [GBER: The Mathematical Foundation](gber.md)
- [Theoretical Aspects of SNIC](theoretical_aspects.md)
- [Future Directions for SNIC](future_directions.md)

*Last Updated: August 10, 2024*
