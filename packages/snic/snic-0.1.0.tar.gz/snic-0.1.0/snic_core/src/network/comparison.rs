use crate::common_types::BaseInt;

/// Generate pairwise combinations of indices for given size
pub fn generate_expansion_mould_for(size: BaseInt) -> Vec<(BaseInt, BaseInt)> {
    let mut comparison_indices: Vec<(BaseInt, BaseInt)> = vec!();
    for left_pointer in 0..(size-1) {
        for right_pointer in (left_pointer+1)..size {
            comparison_indices.push((left_pointer, right_pointer));
        };
    };
    comparison_indices
}


/// Retrieve elements by pairwaise indices mould
pub fn convert_to_comparisons<T: Clone>(
    matchup_result: &[T],
    mould: &[(BaseInt, BaseInt)],
) -> Vec<(T, T)> {
    mould.iter().map(|(lix, rix)| {
        (
            matchup_result[*lix as usize].clone(),
            matchup_result[*rix as usize].clone()
        )
    }).collect()
}


#[cfg(test)]
mod test_matchup_result_conversion {
    use super::convert_to_comparisons;
    use crate::common_types::BaseInt;
    const MATCHUP_SIZE: BaseInt = u8::MAX as BaseInt;

    #[test]
    fn test_elements_retrieval() {
        let indices = (0, MATCHUP_SIZE - 1);
        let values = indices;
        let mould: &[(BaseInt, BaseInt)] = &[indices];
        let matchup_results = &(0..MATCHUP_SIZE).collect::<Vec<BaseInt>>()[..];
        assert_eq!(convert_to_comparisons(matchup_results, mould), vec![values]);
    }
}


#[cfg(test)]
mod test_mould_generation {
    use super::generate_expansion_mould_for;
    use crate::common_types::{BaseInt, InputInt};
    const MATCHUP_SIZE: BaseInt = u8::MAX as BaseInt;

    #[test]
    fn correct_number_of_pairs() {
        
        let expected_pairs_number: InputInt = (MATCHUP_SIZE as InputInt * (MATCHUP_SIZE as InputInt - 1)) / 2;
        assert_eq!(
            expected_pairs_number as usize,
            generate_expansion_mould_for(MATCHUP_SIZE).len()
        )
    }

    #[test]
    fn expand_3() {
        assert_eq!(
            generate_expansion_mould_for(3),
            vec![(0, 1), (0, 2), (1, 2)],
        );
    }

    #[test]
    fn expand_4() {
        assert_eq!(
            generate_expansion_mould_for(4),
            vec![
                (0, 1), (0, 2), (0, 3),
                (1, 2), (1, 3),
                (2, 3)
            ],
        );
    }
}
