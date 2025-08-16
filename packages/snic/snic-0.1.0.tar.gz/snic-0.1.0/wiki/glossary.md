# SNIC Glossary

This glossary provides definitions for key terms used in the context of the Sparse Network of Idempotent Comparisons (SNIC) algorithm. These definitions are consistent with the information presented throughout the SNIC wiki.

## A

**Adaptive Connection Strategy**: A proposed approach for optimizing the hub-and-spoke model in SNIC, where the number and nature of connections between subnetworks are dynamically adjusted based on network characteristics.

## B

**Base**: In SNIC, the chosen number that determines the size of matchups and influences the structure of the network. It's a fundamental parameter in the Generalized Base Exponential Representation (GBER).

**Base-sized Matchup**: A comparison group in SNIC containing exactly 'b' elements, where 'b' is the chosen base for the SNIC system.

## C

**Coefficient**: In GBER, the multiplier for each term in the representation. In the context of SNIC, coefficients determine the number of subnetworks of a particular size.

**Comparison Graph**: A directed graph constructed from the pairwise comparisons derived from SNIC matchups, where nodes represent elements and edges represent win relationships.

## D

**Directed Graph**: A graph where edges have a direction, used in SNIC to represent the results of comparisons (e.g., A beats B).

## G

**Generalized Base Exponential Representation (GBER)**: A mathematical method for representing integers as sums of powers of a chosen base, fundamental to SNIC's network structure.

**Global Ranking**: The overall ranking of all elements across all subnetworks in a SNIC system.

## H

**Hub**: In the hub-and-spoke model of SNIC, the largest subnetwork that connects to all other subnetworks (spokes) to facilitate global ranking.

**Hub-and-Spoke Model**: The proposed structure for connecting subnetworks in SNIC, where one subnetwork (the hub) connects to all others (the spokes).

## I

**Idempotent Comparison**: In SNIC, a comparison that yields the same result regardless of how many times it's performed, ensuring consistency within matchups.

## L

**Local Ranking**: The ranking of elements within a single subnetwork in SNIC.

## M

**Matchup**: A group of elements in SNIC that are compared together. The size of a matchup is determined by the chosen base.

**Matchup Generation**: The process in SNIC of creating groups of elements for comparison, based on the network structure and GBER decomposition.

## N

**Network Diameter**: In SNIC, the maximum distance between any two elements in the network, considering both within-subnetwork and inter-subnetwork connections.

## P

**Pairwise Comparison**: A comparison between two elements, derived from the results of a base-sized matchup in SNIC.

**Power**: In GBER, the exponent applied to the base in each term. In SNIC, powers determine the sizes of subnetworks.

## R

**Remainder**: In GBER and SNIC, the elements left over after forming full-sized subnetworks based on the GBER decomposition.

## S

**Sparsity**: A key property of SNIC, referring to the significantly reduced number of comparisons compared to exhaustive pairwise comparison methods.

**Spoke**: In the hub-and-spoke model of SNIC, any subnetwork that connects to the hub subnetwork.

**Stride**: In SNIC's matchup generation algorithm, the distance between elements grouped into a matchup within a subnetwork.

**Subnetwork**: A group of elements in SNIC that share certain comparison properties, derived from a term in the GBER decomposition of the total number of elements.

## T

**Transitive Comparison**: In SNIC, if A beats B and B beats C, then A is inferred to beat C within the same matchup.

This glossary covers the key terms used in describing and understanding the SNIC algorithm. As SNIC continues to develop, new terms may be added or existing definitions refined to reflect the latest advancements in the technology.

*Last Updated: August 10, 2024*
