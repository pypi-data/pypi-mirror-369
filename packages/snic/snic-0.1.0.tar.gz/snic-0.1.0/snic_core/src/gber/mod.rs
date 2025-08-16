//! Generalized Base Exponential Representation (GBER)
//! Key aspects of GBER in SNIC:
//! 1. **Number Representation**: GBER represents any non-negative integer N as a sum of powers of a chosen base b:
//!    N = c₁b^p₁ + c₂b^p₂ + ... + cₖb^pₖ + r
//!    Where 0 < cᵢ < b, p₁ > p₂ > ... > pₖ ≥ 0, and 0 ≤ r < b
//!
//! 2. **Uniqueness**: For any given base b and number N, there is only one correct GBER representation.
//!
//! 3. **Completeness**: GBER can represent any non-negative integer for any base b > 1.

use crate::common_types::{BaseInt, InputInt};
use crate::common_utilities;

/// GBER of a number.
#[derive(Default, Debug, Clone, PartialEq)]
pub struct Decomposition {
    /// The base against which the number is decomposed.
    pub base: BaseInt,
    /// Flattened term components as base exponents.
    pub component_powers: Vec<u8>,
    /// The last 0-power term as a remainder.
    pub remainder: BaseInt,
}

impl Decomposition {
    pub fn new(decimal_number: InputInt, base: BaseInt) -> Result<Self, &'static str> {
        if base < 2 {
            return Err("The base must be greater than 1.");
        }
        let mut remainder = decimal_number;
        let mut component_collections: Vec<Vec<u8>> = vec![];
        loop {
            let decomposition_step_result = get_max_components_from(remainder, base);
            match decomposition_step_result {
                None => break,
                Some((transitive_remainder, components)) => {
                    remainder = transitive_remainder;
                    component_collections.push(components);
                }
            };
        }
        Ok(Self {
            base,
            remainder: remainder as BaseInt,
            component_powers: component_collections.into_iter().flatten().collect(),
        })
    }

    pub fn stream_all_components(&self) -> impl Iterator<Item = InputInt> + '_ {
        self.component_powers
            .iter()
            .map(|power| self.calculate_single_component(*power))
    }

    /// Present the component as its regular integer variant
    pub fn calculate_single_component(&self, component_power: u8) -> InputInt {
        (self.base as InputInt).pow(component_power as u32)
    }

    /// Return the original integer value of the GBER.
    pub fn to_decimal(&self) -> InputInt {
        self.stream_all_components().sum::<InputInt>() + self.remainder as InputInt
    }
}

fn get_max_components_from(number: InputInt, base: BaseInt) -> Option<(InputInt, Vec<u8>)> {
    // The log will always be >= 1,
    // since the size is always greater than the base
    if number < base.into() {
        return None;
    }
    let exponent = common_utilities::integer_log(number, base);

    // Always: number >= component >= base > coefficient
    let component = (base as InputInt).pow(exponent as u32);
    let coefficient: BaseInt = (number / component) as BaseInt;
    let full_term: InputInt = component * coefficient as InputInt;
    let temporary_remainder: InputInt = number - full_term;
    Some((
        temporary_remainder,
        (0..coefficient).map(|_| exponent).collect(),
    ))
}
