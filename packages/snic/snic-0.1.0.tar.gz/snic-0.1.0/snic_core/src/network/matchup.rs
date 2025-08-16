//! Generation of matchups for a network based on a GBER of it's size.
use crate::common_types::{BaseInt, InputInt};
use crate::common_utilities;
use crate::gber;
use std::collections::VecDeque;
use std::iter::zip;

/// Calculate the number of matchups for a subnetwork of a given size.
/// Since it can be derived mathematically, this is more useful to do
/// than to iterate through the matchups.
pub fn calculate_matchups_number_for(subnetwork_size: InputInt, base: BaseInt) -> u64 {
    let initiator_items: u64 = (subnetwork_size / base as InputInt).into();
    let matchups_per_item = common_utilities::integer_log(subnetwork_size, base);
    initiator_items * matchups_per_item as u64
}

/// Calculate the number of comparisons for a given number of matchups.
/// Since the number of comparisons is a direct function of the number of matchups,
/// this is more useful to do than to iterate through the matchups.
pub fn calculate_comparisons_number_for(matchups_number: u64, base: BaseInt) -> u64 {
    let base: InputInt = base.into();
    let per_matchup: InputInt = base * (base - 1) / 2;
    matchups_number * per_matchup as u64
}

/// Iterator for generating the matchups of a subnetwork.
/// References elements of the subnetwork by their index.
/// Indices are 0-based and global to the whole network.
#[derive(Default, Debug)]
pub struct SubnetworkMatchupIterator {
    /// Should be an integer component of a GBER term.
    pub network_size: InputInt,
    /// Coincides with the base of the GBER.
    pub matchup_size: BaseInt,
    /// Index offset for the items in the subnetwork.
    pub offset: InputInt,
    level: u8,
    // Current item, exclusive end item
    section_states: Vec<(InputInt, InputInt)>,
    section_group_head: usize,
}

impl SubnetworkMatchupIterator {
    pub fn new(
        network_size: InputInt,
        matchup_size: BaseInt,
        offset: InputInt,
    ) -> Result<Self, String> {
        Ok(Self {
            network_size,
            matchup_size,
            offset,
            ..Default::default()
        })
    }
    fn init_level(&mut self) -> Option<()> {
        self.level += 1;
        let sections_number = self.calculate_sections_number();
        if sections_number > self.network_size {
            return None;
        }
        self.section_states.clear();
        let section_size: InputInt = self.network_size / sections_number;
        let mut head: InputInt = 0;
        let rangetails = (section_size..self.network_size + 1).filter(|&ix| ix % section_size == 0);
        self.section_states = rangetails
            .map(|tail| {
                let section = (head, tail);
                head += section_size;
                section
            })
            .collect();
        self.section_group_head = 0;
        Some(())
    }

    fn calculate_sections_number(&self) -> InputInt {
        (self.matchup_size as InputInt).pow(self.level as InputInt)
    }
    fn increment_internal_section_pointer(&mut self, index: usize) {
        self.section_states[index].0 += 1;
    }
    fn increment_group_head_if_exhausted(&mut self) {
        let (ctrlhead, ctrltail) = self.section_states[self.section_group_head];
        if ctrltail == ctrlhead {
            self.section_group_head += self.matchup_size as usize;
        };
    }
}

impl Iterator for SubnetworkMatchupIterator {
    type Item = Vec<InputInt>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.section_group_head >= self.section_states.len() {
            self.init_level()?
        };
        let group_size = self.matchup_size as usize;
        let sections = self.section_states.clone();

        let selected_sections = sections
            .iter()
            .enumerate()
            .skip(self.section_group_head)
            .take(group_size);
        let matchup: Vec<InputInt> = selected_sections
            .map(|(ix, section)| {
                let old_head = section.0;
                self.increment_internal_section_pointer(ix);
                old_head + self.offset
            })
            .collect();
        self.increment_group_head_if_exhausted();

        Some(matchup)
    }
}

/// Iterator for generating the matchups of the whole network.
/// Generates intra-subnetwork matchups first,
/// then inter-subnetwork matchups,
/// then remainder matchups.
#[derive(Default, Debug)]
pub struct LocalMatchupsManager {
    pub network_gber: gber::Decomposition,
    pub subnetwork_iterators: VecDeque<SubnetworkMatchupIterator>,
    pub intersubnetwork_matchups: VecDeque<Vec<InputInt>>,
}

impl LocalMatchupsManager {
    pub fn new(network_gber: gber::Decomposition) -> Self {
        let mut rolling_offset: InputInt = 0;
        let subnetwork_iterators = network_gber
            .stream_all_components()
            .map(|sn_size| {
                let iter =
                    SubnetworkMatchupIterator::new(sn_size, network_gber.base, rolling_offset).unwrap();
                rolling_offset += sn_size;
                iter
            })
            .collect();
        let intersubnetwork_matchups = create_intersubnetwork_matchups(&network_gber);
        Self {
            network_gber,
            subnetwork_iterators,
            intersubnetwork_matchups,
        }
    }
}

fn create_intersubnetwork_matchups(decomposition: &gber::Decomposition) -> VecDeque<Vec<InputInt>> {
    let component_pairs: Vec<(InputInt, u8)> = zip(
        decomposition.stream_all_components(),
        decomposition.component_powers.clone(),
    )
    .collect();
    let seat_allocations = matchup_allocations_for(&component_pairs, decomposition.base);
    let mut component_iterator = component_pairs.iter();

    let mut total_hub_seats: BaseInt = seat_allocations
        .iter()
        .map(|(hs, _)| hs.to_owned())
        .sum::<BaseInt>();
    if decomposition.remainder > 0 {
        total_hub_seats += decomposition.base - decomposition.remainder;
    }
    if total_hub_seats == 0 {
        return VecDeque::new();
    }

    let mut index_offset: InputInt = 0;
    let mut hub_seat_offset: BaseInt = 0;
    let (hub_network_size, _) = component_iterator.next().unwrap();
    let reserved_hub_seats =
        take_elements_uniformly(*hub_network_size, total_hub_seats, index_offset)
            .collect::<Vec<InputInt>>();
    index_offset += hub_network_size;

    let mut inter_matchups: VecDeque<Vec<InputInt>> = zip(component_iterator, seat_allocations)
        .map(|((spoke_size, _), (hub_seats, spoke_seats))| {
            let reserved_spoke_seats_stream =
                take_elements_uniformly(*spoke_size, spoke_seats, index_offset);
            let current_hub_seats =
                get_vector_slice_from(&reserved_hub_seats, hub_seat_offset, hub_seats);
            index_offset += spoke_size;
            hub_seat_offset += hub_seats;
            current_hub_seats
                .into_iter()
                .chain(reserved_spoke_seats_stream)
                .collect::<Vec<InputInt>>()
        })
        .collect();

    if decomposition.remainder == 0 {
        return inter_matchups;
    }
    let remainder_hub_seats = get_vector_slice_from(
        &reserved_hub_seats,
        hub_seat_offset,
        decomposition.base - decomposition.remainder,
    );
    let remainder_elements = index_offset..(index_offset + decomposition.remainder as InputInt);
    let remainder_matchup = remainder_elements.chain(remainder_hub_seats).collect();
    inter_matchups.push_back(remainder_matchup);
    inter_matchups
}

fn get_vector_slice_from<T: Clone>(view: &[T], start: BaseInt, quantity: BaseInt) -> Vec<T> {
    let slice_range = start as usize..(start + quantity) as usize;
    Vec::from(&view[slice_range])
}

fn allocate_matchup_seats_for(
    hub_exponent: u8,
    spoke_exponent: u8,
    matchup_size: BaseInt,
) -> (BaseInt, BaseInt) {
    if matchup_size == 2 {
        return (1, 1);
    };
    let total_ratio_pool = hub_exponent + spoke_exponent;
    let hub_seats: BaseInt = (matchup_size * hub_exponent as BaseInt) / total_ratio_pool as BaseInt;
    let spoke_seats: BaseInt = matchup_size - hub_seats;
    (hub_seats, spoke_seats)
}

fn matchup_allocations_for(
    network_size_components: &[(InputInt, u8)],
    matchup_size: BaseInt,
) -> Vec<(BaseInt, BaseInt)> {
    let mut termiter = network_size_components.iter().filter(|comp| comp.1 > 0);
    // First term is the hub
    let hub_exponent = termiter.next().unwrap().1;
    termiter
        .map(move |comp| allocate_matchup_seats_for(hub_exponent, comp.1, matchup_size))
        .collect()
}

fn take_elements_uniformly(
    network_size: InputInt,
    quantity: BaseInt,
    offset: InputInt,
) -> impl Iterator<Item = InputInt> {
    let window_size: InputInt = network_size
        .checked_div(quantity as InputInt)
        .ok_or("Division by zero")
        .expect("Cannot take 0 elements");
    (0..network_size)
        .filter(move |ix| ix % window_size == 0)
        .map(move |ix| ix + offset)
        .take(quantity.into())
}

#[cfg(test)]
mod test_match_count {
    use crate::gber::Decomposition;
    use super::calculate_matchups_number_for;
    use super::LocalMatchupsManager;
    use crate::common_types::{BaseInt, InputInt};
    use std::collections::HashSet;
    const NETWORK_SIZE: InputInt = BaseInt::MAX as InputInt;
    const MATCH_SIZE: BaseInt = 2;

    #[test]
    fn matches_are_unique() {
        let decomposition =
            Decomposition::new(NETWORK_SIZE, MATCH_SIZE).expect("Invalid decomposition values");
        let network = LocalMatchupsManager::new(decomposition);
        let matchups = network.subnetwork_iterators
            .into_iter().flatten().collect::<Vec<Vec<InputInt>>>();
        let matchups_length = matchups.len();
        let unique_matchups = matchups.into_iter().collect::<HashSet<Vec<InputInt>>>();
        assert_eq!(matchups_length, unique_matchups.len());
    }


    #[test]
    fn special_2_base() {
        let decomposition =
            Decomposition::new(NETWORK_SIZE, MATCH_SIZE).expect("Invalid decomposition values");
        let math_calculation = decomposition.stream_all_components()
            .map(|comp_size| calculate_matchups_number_for(comp_size, MATCH_SIZE))
            .sum::<u64>();
        let network = LocalMatchupsManager::new(decomposition);
        let counted_subnetwork_matchups = network.subnetwork_iterators
            .into_iter().flatten().map(|_| 1u64).sum::<u64>();
        assert_eq!(math_calculation, counted_subnetwork_matchups);
    }

}


#[cfg(test)]
mod test_get_vector_slice_from {
    use super::get_vector_slice_from;
    const ZEROS: [i32; 5] = [0, 0, 0, 0, 0];

    #[test]
    fn full_slice() {
        assert_eq!(
            &ZEROS[..],
            &get_vector_slice_from(&ZEROS, 0, ZEROS.len() as u16)[..],
        )
    }

    #[test]
    fn slice_length() {
        assert_eq!(
            3,
            get_vector_slice_from(&ZEROS, 0, 3).len(),
        )
    }
}

#[cfg(test)]
mod test_matchup_allocations_for {
    use super::{matchup_allocations_for, BaseInt, InputInt};
    const SHORT_SLICE: &[(InputInt, u8)] = &[(100, 2), (10, 1)];
    const MID_SLICE: &[(InputInt, u8)] = &[(1000, 3), (100, 2), (10, 1)];
    const LONGER_SLICE: &[(InputInt, u8)] = &[
        (1000, 3),
        //
        (1000, 3),
        (1000, 3),
        (1000, 3),
        (1000, 3),
        (100, 2),
        (100, 2),
        (100, 2),
        (100, 2),
        (10, 1),
        (10, 1),
        (10, 1),
        (10, 1),
    ];


    #[test]
    fn base2() {
        let base = 2 as InputInt;
        let slice = &[(base.pow(10), 10u8), (base.pow(10), 10u8), (base, 1u8)];
        for allocation in matchup_allocations_for(slice, base as BaseInt) {
            assert_eq!(allocation, (1 as BaseInt, 1 as BaseInt))
        }
    }


    #[test]
    fn seat_allocation_equivalence() {
        let base = 10;
        for slice in [SHORT_SLICE, MID_SLICE, LONGER_SLICE] {
            let allocations = matchup_allocations_for(slice, base);
            assert_eq!(
                allocations.into_iter().map(|(a, b)| a + b).sum::<BaseInt>(),
                (slice.len() as BaseInt - 1) * base,
            )
        }
    }

    #[test]
    fn simple_10_base_components() {
        assert_eq!(matchup_allocations_for(SHORT_SLICE, 10), vec![(6, 4)]);
        assert_eq!(matchup_allocations_for(MID_SLICE, 10), vec![(6, 4), (7, 3)]);
        assert_eq!(
            matchup_allocations_for(LONGER_SLICE, 10),
            vec![
                (5, 5),
                (5, 5),
                (5, 5),
                (5, 5),
                (6, 4),
                (6, 4),
                (6, 4),
                (6, 4),
                (7, 3),
                (7, 3),
                (7, 3),
                (7, 3),
            ]
        );
    }
}


#[cfg(test)]
mod test_take_elements_uniformly {
    use super::take_elements_uniformly;

    #[test]
    fn take_2_of_20() {
        assert_eq!(
            take_elements_uniformly(20, 2, 10).collect::<Vec<u32>>(),
            vec![10, 20],
        );
    }
    #[test]
    fn take_2_of_3() {
        assert_eq!(
            take_elements_uniformly(3, 2, 100).collect::<Vec<u32>>(),
            vec![100, 101],
        );
    }
    #[test]
    fn take_5_of_1000() {
        assert_eq!(
            take_elements_uniformly(1001, 5, 1).collect::<Vec<u32>>(),
            vec![1, 201, 401, 601, 801],
        );
    }
}
