use crate::common_types::{BaseInt, InputInt};

/// Calculate the integer logarithm of a number.
/// This had different implementations historically.
pub fn integer_log(number: InputInt, base: BaseInt) -> u8 {
    // The floor of the log base of a number
    (number as f64).log(base as f64).floor() as u8
}
