# SNIC Network Structure

## Introduction

The Sparse Network of Idempotent Comparisons (SNIC) algorithm employs a unique network structure that is fundamental to its efficient ranking approach. This structure, based on the Generalized Base Exponential Representation (GBER), allows SNIC to handle large-scale ranking tasks with remarkable efficiency. In this page, we'll explore the key components and properties of SNIC's network structure.

## Overall Network Architecture

SNIC's network architecture can be conceptualized as a graph:

1. **Nodes**: Each element to be ranked is represented as a node in the graph.
2. **Edges**: Potential comparisons between elements are represented as edges.
3. **Subnetworks**: Groups of nodes that share comparison properties, directly corresponding to terms in the GBER decomposition.
4. **Hub-and-Spoke Structure**: A global connection strategy that links subnetworks together.

This architecture allows SNIC to maintain a sparse yet informative comparison structure, enabling efficient ranking for large datasets.

## Subnetworks in SNIC

Subnetworks are a key feature of SNIC's structure, formed directly from the terms in the GBER decomposition of the total number of elements.

### Definition and Properties

1. **Definition**: A subnetwork is a group of elements within the SNIC network that share certain comparison properties.
2. **Size**: Each subnetwork size corresponds to a power of the chosen base in the GBER decomposition.
3. **Quantity**: The coefficient of each term in the GBER decomposition determines how many subnetworks of that size are created.

### Example

For a base-3 SNIC with 80 elements:

GBER decomposition: 80 = 2 × 3^3 + 2 × 3^2 + 2 × 3^1 + 2 × 3^0
                       = 2 × 27 + 2 × 9 + 2 × 3 + 2 × 1

This translates to the following subnetwork structure:
- Two subnetworks of 27 elements each
- Two subnetworks of 9 elements each
- Two subnetworks of 3 elements each
- Two subnetworks of 1 element each

### Importance of Subnetworks

1. **Efficient Local Rankings**: Subnetworks allow for strong local rankings within manageable group sizes.
2. **Parallel Processing Potential**: The independent nature of subnetworks opens possibilities for parallel computation.
3. **Scalability**: As the total number of elements grows, SNIC can simply add more subnetworks without changing its fundamental structure.

[Learn how GBER shapes these subnetworks](gber.md#gber-in-snic)

## Hub-and-Spoke Model

To connect subnetworks and enable global ranking, SNIC employs a hub-and-spoke model.

### Key Features

1. **Hub Selection**: The largest subnetwork is typically designated as the hub.
2. **Spoke Connections**: All other subnetworks (spokes) are connected to the hub through carefully designed matchups.
3. **Balanced Representation**: The number of elements participating in inter-network matchups is determined using a logarithmic scale to ensure fair representation regardless of subnetwork size.

### Inter-Network Matchup Allocation

SNIC uses a log-based allocation strategy for creating matchups between different networks:

1. For hub network H and spoke network S:
   x_H = log_B(|H|)
   x_S = log_B(|S|)
   Ratio = x_H : x_S

2. This ratio determines how many elements from each network participate in the inter-network matchup.

3. When rounding is necessary, SNIC favors the smaller network to ensure its adequate representation.

### Importance of Hub-and-Spoke Model

1. **Global Connectivity**: Enables information flow between subnetworks, allowing for global ranking.
2. **Maintained Sparsity**: Limits the number of inter-network connections, preserving SNIC's overall sparsity.
3. **Scalability**: Provides a consistent method for connecting subnetworks regardless of the total network size.

[Explore how these connections influence SNIC's efficiency](key_properties.md#efficiency-of-snic)

## Path Properties

The structure of SNIC leads to specific path length properties that contribute to its efficiency.

### Within Subnetworks

1. **Maximum Path Length**: In a subnetwork of size b^p, the maximum path length between any two elements is p.
2. **Average Path Length**: Tends to be logarithmic in the size of the subnetwork.
3. **Efficient Information Flow**: These short path lengths allow for quick propagation of ranking information within subnetworks.

### Global Paths

1. **Inter-Subnetwork Paths**: With the hub-and-spoke model, any two elements in different subnetworks are connected by a path through the hub.
2. **Maximum Global Path Length**: At most 3 steps (spoke to hub, within hub, hub to spoke).
3. **Network Diameter**: Equal to the maximum path length within the largest subnetwork plus 2 (for spoke-hub-spoke connections).

## Degree Distribution

The degree distribution in SNIC networks has several notable properties:

1. **Uniformity Within Subnetworks**: In a subnetwork of size b^p, each element participates in exactly p matchups.
2. **Bounded Degree**: The maximum degree (number of comparisons) for any element is limited by the subnetwork size and the number of inter-network connections.
3. **Hub Nodes**: Elements in the hub subnetwork may have a higher degree due to inter-network connections.
4. **Sparsity**: Despite some nodes (especially in the hub) having higher degrees, the overall network remains sparse compared to a complete comparison graph.

## Conclusion

SNIC's network structure, with its subnetworks, hub-and-spoke model, and specific path and degree properties, forms the backbone of its efficient ranking approach. This structure allows SNIC to maintain sparsity while ensuring sufficient connectivity for meaningful global rankings, making it capable of handling large-scale ranking tasks with remarkable efficiency.

## See Also
- [GBER: The Mathematical Foundation](gber.md)
- [SNIC Operational Flow](operational_flow.md)
- [Key Properties of SNIC](key_properties.md)

*Last Updated: August 10, 2024*
